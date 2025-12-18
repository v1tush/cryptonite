import re
import unicodedata

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F

from ciphers.constants import HINT_PRICE
from ciphers.models import CipherHelp, PurchasedHint
from logs.models import SolutionLog


User = get_user_model()


def purchase_hint(user, hint_id):
    with transaction.atomic():
        hint = (
            CipherHelp.objects.select_for_update()
            .select_related('cipher', 'cipher__author')
            .get(id=hint_id)
        )

        buyer = User.objects.select_for_update().get(id=user.id)

        author = User.objects.select_for_update().get(id=hint.cipher.author_id)

        if buyer == author:
            return {
                'success': False,
            }

        if PurchasedHint.objects.filter(user=buyer, hint=hint).exists():
            return {
                'success': False,
            }

        if buyer.money < HINT_PRICE:
            return {
                'success': False,
                'error': 'Недостаточно монет',
                'balance': buyer.money,
                'required': HINT_PRICE,
            }

        last_attempt = SolutionLog.objects.get_last_attempt(
            buyer,
            hint.cipher,
        )
        if last_attempt and last_attempt.correct:
            return {
                'success': False,
                'error': 'Вы уже решили этот шифр',
            }

        User.objects.filter(pk=buyer.pk).update(money=F('money') - HINT_PRICE)
        User.objects.filter(pk=author.pk).update(money=F('money') + HINT_PRICE)

        PurchasedHint.objects.create(
            user=buyer,
            hint=hint,
        )

    return {
        'success': True,
        'hint': {
            'id': hint.id,
            'text': hint.text,
            'order': hint.order,
        },
        'price_paid': HINT_PRICE,
    }


def normalize_answer(answer):
    answer = answer.strip().lower()
    answer = unicodedata.normalize('NFKD', answer)
    answer = ''.join(c for c in answer if not unicodedata.combining(c))
    answer = re.sub(r'[^a-z0-9а-яё\s]', '', answer)
    return re.sub(r'\s+', ' ', answer)
