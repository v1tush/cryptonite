import random

from django.db import transaction
from django.utils import timezone

from ciphers.models import Cipher, CipherDayHistory


def get_approved_ciphers(exclude_used: bool = True):
    qs = Cipher.objects.approved()

    if exclude_used:
        used_ids = CipherDayHistory.objects.values_list(
            'cipher_id',
            flat=True,
        )

    return qs.exclude(id__in=used_ids)


def setting_daily_cipher() -> None:
    today = timezone.localdate()

    with transaction.atomic():
        if CipherDayHistory.objects.filter(date=today).exists():
            return

        available_ciphers = get_approved_ciphers(exclude_used=True)

        if not available_ciphers.exists():
            CipherDayHistory.objects.all().delete()
            available_ciphers = get_approved_ciphers(exclude_used=False)

        if not available_ciphers.exists():
            return

        cipher = random.choice(list(available_ciphers))

        CipherDayHistory.objects.create(
            cipher=cipher,
            date=today,
        )
