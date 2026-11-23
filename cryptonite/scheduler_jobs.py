import random

from django.db import close_old_connections
from django.db.models import Max
from django.utils import timezone

from ciphers.models import Cipher, CipherDayHistory


def select_daily_cipher():
    close_old_connections()
    try:
        today = timezone.localdate()
        if CipherDayHistory.objects.filter(date=today).exists():
            return

        candidates = list(
            Cipher.objects.approved()
            .annotate(
                last_used=Max('cipher_day_history__date'),
            )
            .values_list('pk', 'last_used')
        )
        fresh = [pk for pk, last_used in candidates if last_used is None]
        if fresh:
            cipher_id = random.choice(fresh)
        elif candidates:
            cipher_id, _ = min(candidates, key=lambda item: item[1])
        else:
            return
        # The unique date constraint also covers overlapping job runs.
        CipherDayHistory.objects.get_or_create(
            date=today,
            defaults={'cipher_id': cipher_id},
        )
    finally:
        close_old_connections()
