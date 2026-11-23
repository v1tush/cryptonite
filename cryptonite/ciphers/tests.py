import json
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from threading import Barrier
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError, close_old_connections, connections
from django.test import (
    TestCase,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import reverse

from ciphers.constants import HINT_PRICE, REWARD_VALUES
from ciphers.models import Cipher, CipherHelp, PurchasedHint
from ciphers.services import GameRuleError, purchase_hint, submit_solution
from feedback.models import Feedback
from logs.models import SolutionLog

User = get_user_model()


def create_user(username, **kwargs):
    return User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        **kwargs,
    )


def create_cipher(author, **kwargs):
    fields = {
        'title': 'Cipher test',
        'encrypted_phrase': 'KHOOR',
        'answer_phrase': 'Hello World',
        'description': 'A Caesar shift example. ' * 5,
        'difficulty': 1,
        'status': 'approved',
        'attempt_limit': 2,
    }
    return Cipher.objects.create(author=author, **(fields | kwargs))


class GameplayTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = create_user('author')
        cls.player = create_user('player', money=HINT_PRICE + 10)
        cls.staff = create_user('moderator', is_staff=True)
        cls.cipher = create_cipher(cls.author)
        cls.hint = CipherHelp.objects.create(
            cipher=cls.cipher, text='Shift by 3'
        )

    def setUp(self):
        media = TemporaryDirectory()
        self.addCleanup(media.cleanup)
        settings = override_settings(MEDIA_ROOT=media.name)
        settings.enable()
        self.addCleanup(settings.disable)
        self.client.force_login(self.player)
        self.url = self.cipher.get_absolute_url()

    def answer(self, text):
        return self.client.post(self.url, {'attempted_answer': text})

    def buy(self, hint_id, url=None):
        return self.client.post(
            url or self.url,
            {'hint_id': hint_id},
            content_type='application/json',
            headers={'x-requested-with': 'XMLHttpRequest'},
        )

    def test_wrong_then_correct_then_resubmission(self):
        self.assertRedirects(
            self.answer('Wrong'), self.url, fetch_redirect_response=False
        )
        wrong = SolutionLog.objects.get()
        self.assertEqual(
            (wrong.attempts_used, wrong.correct, wrong.score), (1, False, 0)
        )
        self.player.refresh_from_db()
        self.assertEqual(
            (self.player.xp, self.player.money), (0, HINT_PRICE + 10)
        )
        self.assertEqual(self.answer('  !HéLLo,   WORLD!  ').status_code, 302)
        self.assertEqual(self.answer('hello world').status_code, 200)
        solution = SolutionLog.objects.get(correct=True)
        self.assertEqual(solution.attempts_used, 2)
        self.assertEqual(SolutionLog.objects.count(), 2)
        self.assertEqual(
            solution.score, REWARD_VALUES['score_for_correct_solution']
        )
        self.player.refresh_from_db()
        self.assertEqual(
            self.player.xp, REWARD_VALUES['xp_for_correct_solution']
        )
        self.assertEqual(
            self.player.money,
            HINT_PRICE + 10 + REWARD_VALUES['money_for_correct_solution'],
        )
        self.assertEqual(self.player.solved_ciphers_count, 1)

    def test_attempt_limit_cannot_be_exceeded(self):
        self.assertEqual(self.answer('wrong').status_code, 302)
        self.assertEqual(self.answer('wrong again').status_code, 302)
        self.assertEqual(self.answer('hello world').status_code, 200)
        self.assertEqual(SolutionLog.objects.count(), 2)
        self.assertFalse(SolutionLog.objects.filter(correct=True).exists())

    def test_invalid_answers_do_not_consume_attempts(self):
        for answer in ('', '!!!', 'a' * 101):
            with self.subTest(answer=answer):
                self.assertEqual(self.answer(answer).status_code, 200)
        self.assertFalse(SolutionLog.objects.exists())

    def test_cyrillic_short_i_is_not_normalized_to_i(self):
        Cipher.objects.filter(pk=self.cipher.pk).update(answer_phrase='мой')
        self.assertEqual(self.answer('мои').status_code, 302)
        self.assertEqual(self.answer('МОИ\u0306').status_code, 302)
        self.assertEqual(
            list(
                SolutionLog.objects.order_by('attempts_used').values_list(
                    'correct', flat=True
                )
            ),
            [False, True],
        )

    def test_author_and_staff_cannot_earn_rewards_from_previews(self):
        self.client.force_login(self.author)
        self.assertEqual(self.answer('Hello World').status_code, 200)
        Cipher.objects.filter(pk=self.cipher.pk).update(status='pending')
        self.client.force_login(self.staff)
        self.assertContains(self.client.get(self.url), self.hint.text)
        self.assertEqual(self.answer('Hello World').status_code, 200)
        self.assertFalse(SolutionLog.objects.exists())

    def test_purchase_transfers_coins_once_and_reveals_text(self):
        self.assertNotContains(self.client.get(self.url), self.hint.text)
        result = self.buy(str(self.hint.pk)).json()
        self.assertTrue(result['success'])
        self.assertEqual(result['hint']['text'], self.hint.text)
        self.assertEqual(result['new_balance'], 10)
        self.assertFalse(self.buy(self.hint.pk).json()['success'])
        self.assertEqual(PurchasedHint.objects.count(), 1)
        self.player.refresh_from_db()
        self.author.refresh_from_db()
        self.assertEqual(
            (self.player.money, self.author.money), (10, HINT_PRICE)
        )
        self.assertContains(self.client.get(self.url), self.hint.text)

    def test_purchase_rolls_back_transfer_if_receipt_cannot_be_saved(self):
        with patch.object(
            PurchasedHint.objects, 'create', side_effect=IntegrityError
        ):
            with self.assertRaises(IntegrityError):
                purchase_hint(
                    user=self.player,
                    cipher_id=self.cipher.pk,
                    hint_id=self.hint.pk,
                )
        self.player.refresh_from_db()
        self.author.refresh_from_db()
        self.assertEqual(
            (self.player.money, self.author.money), (HINT_PRICE + 10, 0)
        )
        self.assertFalse(PurchasedHint.objects.exists())

    def test_purchase_requires_funds_and_disallows_author_or_solver(self):
        User.objects.filter(pk=self.player.pk).update(money=HINT_PRICE - 1)
        result = self.buy(self.hint.pk).json()
        self.assertEqual(
            (result['success'], result['balance']), (False, HINT_PRICE - 1)
        )
        self.assertEqual(self.answer('hello world').status_code, 302)
        self.assertFalse(self.buy(self.hint.pk).json()['success'])
        self.client.force_login(self.author)
        self.assertFalse(self.buy(self.hint.pk).json()['success'])
        self.assertFalse(PurchasedHint.objects.exists())
        self.author.refresh_from_db()
        self.assertEqual(self.author.money, 0)

    def test_purchase_rejects_wrong_cipher_inaccessible_cipher_and_bad_payload(
        self,
    ):
        other = create_cipher(self.author, status='hidden')
        other_hint = CipherHelp.objects.create(cipher=other, text='Private')
        self.assertEqual(self.buy(other_hint.pk).status_code, 404)
        self.assertEqual(
            self.buy(other_hint.pk, other.get_absolute_url()).status_code, 404
        )
        self.assertEqual(self.buy(True).status_code, 400)
        self.assertFalse(PurchasedHint.objects.exists())

    def test_only_author_can_edit_even_if_other_user_is_staff(self):
        edit = reverse('ciphers:edit_cipher', args=[self.cipher.pk])
        for user in (self.player, self.staff):
            self.client.force_login(user)
            self.assertEqual(self.client.get(edit).status_code, 404)
        self.client.force_login(self.author)
        self.assertEqual(self.client.get(edit).status_code, 200)
        data = {
            'title': 'Updated',
            'description': self.cipher.description,
            'encrypted_phrase': self.cipher.encrypted_phrase,
            'answer_phrase': self.cipher.answer_phrase,
            'difficulty': self.cipher.difficulty,
            'attempt_limit': self.cipher.attempt_limit,
        }
        other = create_cipher(self.player)
        foreign_hint = CipherHelp.objects.create(cipher=other, text='Foreign')
        invalid = data | {
            'hints_payload': json.dumps(
                [{'id': foreign_hint.pk, 'order': 1, 'text': 'Foreign'}],
            ),
        }
        reply = self.client.post(
            edit, invalid, headers={'x-requested-with': 'XMLHttpRequest'}
        )
        self.assertFalse(reply.json()['success'])
        self.cipher.refresh_from_db()
        self.assertEqual(
            (self.cipher.title, self.cipher.status),
            ('Cipher test', 'approved'),
        )
        self.assertEqual(self.client.post(edit, data).status_code, 302)
        self.cipher.refresh_from_db()
        self.assertEqual(
            (self.cipher.title, self.cipher.status), ('Updated', 'pending')
        )

    def test_only_staff_can_moderate_and_approve_answers_complaints(self):
        Cipher.objects.filter(pk=self.cipher.pk).update(status='pending')
        complaint = Feedback.objects.create(
            author=self.player,
            cipher=self.cipher,
            text='Clarify',
        )
        self.client.force_login(self.author)
        self.assertEqual(
            self.client.post(
                self.url, {'moderation_action': 'approve'}
            ).status_code,
            403,
        )
        self.client.force_login(self.staff)
        self.assertEqual(
            self.client.post(
                self.url, {'moderation_action': 'invalid'}
            ).status_code,
            400,
        )
        self.assertEqual(
            self.client.post(
                self.url, {'moderation_action': 'approve'}
            ).status_code,
            302,
        )
        self.assertEqual(
            self.client.post(
                self.url, {'moderation_action': 'reject'}
            ).status_code,
            400,
        )
        self.cipher.refresh_from_db()
        complaint.refresh_from_db()
        self.assertEqual(
            (self.cipher.status, complaint.status), ('approved', 'answered')
        )

    def test_hint_edit_preserves_purchases_and_checks_ownership(self):
        self.assertTrue(self.buy(self.hint.pk).json()['success'])
        url = reverse('ciphers:save_cipher_hints')
        data = {
            'cipher_id': self.cipher.pk,
            'hints': [{'id': self.hint.pk, 'text': 'Edited hint', 'order': 1}],
        }
        self.assertEqual(
            self.client.post(
                url, data, content_type='application/json'
            ).status_code,
            404,
        )
        self.client.force_login(self.author)
        self.assertEqual(
            self.client.post(
                url, data, content_type='application/json'
            ).status_code,
            200,
        )
        self.hint.refresh_from_db()
        self.cipher.refresh_from_db()
        self.assertEqual(self.hint.text, 'Edited hint')
        self.assertEqual(self.cipher.status, 'pending')
        self.assertTrue(
            PurchasedHint.objects.filter(
                hint=self.hint, user=self.player
            ).exists()
        )

    def test_failing_to_credit_reward_rolls_back_log_and_solved_count(self):
        rewards = REWARD_VALUES | {'money_for_correct_solution': -10000}
        with patch('ciphers.services.REWARD_VALUES', rewards):
            with self.assertRaises(IntegrityError):
                submit_solution(
                    user=self.player,
                    cipher_id=self.cipher.pk,
                    answer='Hello World',
                )
        self.assertFalse(SolutionLog.objects.exists())
        self.player.refresh_from_db()
        self.assertEqual(
            (self.player.xp, self.player.solved_ciphers_count), (0, 0)
        )


@skipUnlessDBFeature('has_select_for_no_key_update')
class ConcurrentGameplayTests(TransactionTestCase):
    def setUp(self):
        self.author = create_user('author')
        self.player = create_user('player', money=HINT_PRICE)
        self.cipher = create_cipher(self.author, attempt_limit=1)

    def race(self, *calls):
        barrier = Barrier(len(calls), timeout=10)

        def run(call):
            close_old_connections()
            try:
                with connections['default'].cursor() as cursor:
                    cursor.execute("SET lock_timeout = '5s'")
                barrier.wait()
                return call()
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=len(calls)) as pool:
            futures = [pool.submit(run, call) for call in calls]
            return [future.result(timeout=15) for future in futures]

    def submit(self, answer):
        try:
            return submit_solution(
                user=self.player,
                cipher_id=self.cipher.pk,
                answer=answer,
            ).correct
        except GameRuleError:
            return None

    def test_concurrent_correct_answers_reward_only_once(self):
        Cipher.objects.filter(pk=self.cipher.pk).update(attempt_limit=None)

        def solve():
            return self.submit('Hello World')

        self.assertCountEqual(self.race(solve, solve), [True, None])
        self.assertEqual(SolutionLog.objects.count(), 1)
        self.player.refresh_from_db()
        self.assertEqual(
            self.player.xp, REWARD_VALUES['xp_for_correct_solution']
        )
        self.assertEqual(
            self.player.money,
            HINT_PRICE + REWARD_VALUES['money_for_correct_solution'],
        )
        self.assertEqual(self.player.solved_ciphers_count, 1)

    def test_concurrent_wrong_answers_respect_last_attempt(self):
        self.assertCountEqual(
            self.race(
                lambda: self.submit('wrong'), lambda: self.submit('wrong')
            ),
            [False, None],
        )
        self.assertEqual(SolutionLog.objects.get().attempts_used, 1)

    def test_simultaneous_rewards_for_different_ciphers_add_up(self):
        other = create_cipher(self.author)

        def solve(cipher):
            return submit_solution(
                user=self.player,
                cipher_id=cipher.pk,
                answer='Hello World',
            ).correct

        self.assertEqual(
            self.race(lambda: solve(self.cipher), lambda: solve(other)),
            [True, True],
        )
        self.player.refresh_from_db()
        self.assertEqual(
            self.player.xp, REWARD_VALUES['xp_for_correct_solution'] * 2
        )
        self.assertEqual(
            self.player.money,
            HINT_PRICE + REWARD_VALUES['money_for_correct_solution'] * 2,
        )
        self.assertEqual(self.player.solved_ciphers_count, 2)

    def test_parallel_purchases_cannot_spend_same_balance_twice(self):
        other = create_cipher(self.author)
        first = CipherHelp.objects.create(cipher=self.cipher, text='first')
        second = CipherHelp.objects.create(cipher=other, text='second')

        def buy(hint):
            return purchase_hint(
                user=self.player,
                cipher_id=hint.cipher_id,
                hint_id=hint.pk,
            )['success']

        self.assertCountEqual(
            self.race(lambda: buy(first), lambda: buy(second)), [True, False]
        )
        self.assertEqual(PurchasedHint.objects.count(), 1)
        self.player.refresh_from_db()
        self.author.refresh_from_db()
        self.assertEqual(
            (self.player.money, self.author.money), (0, HINT_PRICE)
        )

    def test_players_can_buy_each_others_hints_concurrently(self):
        User.objects.filter(pk=self.author.pk).update(money=HINT_PRICE)
        other = create_cipher(self.player)
        first = CipherHelp.objects.create(cipher=self.cipher, text='first')
        second = CipherHelp.objects.create(cipher=other, text='second')

        def buy(user, hint):
            return purchase_hint(
                user=user,
                cipher_id=hint.cipher_id,
                hint_id=hint.pk,
            )['success']

        self.assertEqual(
            self.race(
                lambda: buy(self.player, first),
                lambda: buy(self.author, second),
            ),
            [True, True],
        )
        self.assertEqual(PurchasedHint.objects.count(), 2)
        self.player.refresh_from_db()
        self.author.refresh_from_db()
        self.assertEqual(
            (self.player.money, self.author.money), (HINT_PRICE, HINT_PRICE)
        )
