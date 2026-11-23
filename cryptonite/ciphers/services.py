import re
import unicodedata

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.db.models import F

from ciphers.constants import HINT_PRICE, REWARD_VALUES
from ciphers.models import Cipher, CipherHelp, PurchasedHint
from feedback.models import Feedback
from logs.models import SolutionLog

User = get_user_model()


class GameRuleError(Exception):
    """A request rejected by the rules, not an infrastructure failure."""


def visible_ciphers(user):
    if user.is_staff:
        return Cipher.objects.all()
    return Cipher.objects.filter(
        models.Q(status='approved') | models.Q(author=user),
    )


@transaction.atomic
def submit_solution(*, user, cipher_id, answer):
    # Lock the parent even on the first attempt, when there is no log to lock.
    cipher = (
        visible_ciphers(user)
        .select_for_update(no_key=True)
        .get(
            pk=cipher_id,
        )
    )
    if not cipher.is_published or cipher.author_id == user.pk:
        raise GameRuleError(
            'Можно решать только опубликованные шифры других авторов'
        )
    attempts = SolutionLog.objects.filter(user=user, cipher=cipher)
    if attempts.filter(correct=True).exists():
        raise GameRuleError('Вы уже решили этот шифр')

    last = attempts.order_by('-attempts_used').first()
    used = last.attempts_used if last else 0
    if cipher.attempt_limit is not None and used >= cipher.attempt_limit:
        raise GameRuleError('Лимит попыток исчерпан')

    normalized = normalize_answer(answer)
    if not normalized:
        raise GameRuleError('Введите ответ, содержащий буквы или цифры')
    correct = normalized == normalize_answer(cipher.answer_phrase)
    solution = SolutionLog.objects.create(
        cipher=cipher,
        user=user,
        attempted_answer=answer,
        attempts_used=used + 1,
        correct=correct,
        score=REWARD_VALUES['score_for_correct_solution'] if correct else 0,
    )
    if correct:
        User.objects.filter(pk=user.pk).update(
            xp=F('xp') + REWARD_VALUES['xp_for_correct_solution'],
            money=F('money') + REWARD_VALUES['money_for_correct_solution'],
            solved_ciphers_count=F('solved_ciphers_count') + 1,
        )

    return solution


@transaction.atomic
def purchase_hint(*, user, cipher_id, hint_id):
    cipher = (
        visible_ciphers(user)
        .select_for_update(no_key=True)
        .get(
            pk=cipher_id,
        )
    )
    hint = cipher.hints.get(pk=hint_id)
    if user.pk == cipher.author_id:
        return {'success': False, 'error': 'Это ваша подсказка'}
    if not cipher.is_published:
        return {'success': False, 'error': 'Шифр не опубликован'}

    # A purchase touches two wallets. Acquire them in the same order even
    # when two players are buying hints from each other on different ciphers.
    wallets = {
        wallet.pk: wallet
        for wallet in User.objects.select_for_update(no_key=True)
        .filter(pk__in=[user.pk, cipher.author_id])
        .order_by('pk')
    }
    buyer = wallets[user.pk]
    if PurchasedHint.objects.filter(user=buyer, hint=hint).exists():
        return {'success': False, 'error': 'Вы уже купили эту подсказку'}

    if SolutionLog.objects.filter(
        user=buyer, cipher=cipher, correct=True
    ).exists():
        return {'success': False, 'error': 'Вы уже решили этот шифр'}

    if buyer.money < HINT_PRICE:
        return {
            'success': False,
            'error': 'Недостаточно монет',
            'balance': buyer.money,
            'required': HINT_PRICE,
        }

    User.objects.filter(pk=buyer.pk).update(money=F('money') - HINT_PRICE)
    User.objects.filter(pk=cipher.author_id).update(
        money=F('money') + HINT_PRICE
    )
    PurchasedHint.objects.create(user=buyer, hint=hint)

    return {
        'success': True,
        'message': 'Подсказка куплена',
        'hint': {
            'id': hint.id,
            'text': hint.text,
            'order': hint.order,
        },
        'price_paid': HINT_PRICE,
        'new_balance': buyer.money - HINT_PRICE,
    }


@transaction.atomic
def moderate_cipher(*, user, cipher_id, action):
    if not user.is_staff:
        raise PermissionDenied
    statuses = {'approve': 'approved', 'reject': 'rejected'}
    if action not in statuses:
        raise GameRuleError('Неизвестное действие модерации')

    cipher = Cipher.objects.select_for_update(no_key=True).get(pk=cipher_id)
    if cipher.status != 'pending':
        raise GameRuleError('Шифр уже не на модерации')

    cipher.status = statuses[action]
    cipher.save(update_fields=['status', 'updated_at'])
    if action == 'approve':
        Feedback.objects.received_for_cipher(cipher).update(status='answered')


@transaction.atomic
def save_cipher_hints(*, user, cipher_id, hints):
    cipher = Cipher.objects.select_for_update(no_key=True).get(
        pk=cipher_id,
        author=user,
    )
    existing = {hint.pk: hint for hint in cipher.hints.all()}
    if any(
        hint_id is not None and hint_id not in existing
        for _, _, hint_id in hints
    ):
        raise GameRuleError('Подсказка не принадлежит этому шифру')

    retained = []
    changed = False
    for order, text, hint_id in hints:
        hint = existing.get(hint_id)
        if hint is None:
            hint = CipherHelp.objects.create(
                cipher=cipher,
                order=order,
                text=text,
            )
            changed = True
        elif hint.text != text or hint.order != order:
            hint.text = text
            hint.order = order
            hint.save(update_fields=['text', 'order', 'updated_at'])
            changed = True
        retained.append(hint.pk)

    deleted, _ = cipher.hints.exclude(pk__in=retained).delete()
    if (changed or deleted) and cipher.status != 'pending':
        cipher.status = 'pending'
        cipher.save(update_fields=['status', 'updated_at'])


def normalize_answer(answer):
    answer = unicodedata.normalize('NFKC', answer).casefold()
    # Keep distinct Russian letters, while still accepting accents on Latin text.
    answer = ''.join(
        c if c in 'йё' else unicodedata.normalize('NFKD', c) for c in answer
    )
    answer = ''.join(c for c in answer if not unicodedata.combining(c))
    answer = re.sub(r'[^a-z0-9а-яё\s]', '', answer)
    return re.sub(r'\s+', ' ', answer).strip()
