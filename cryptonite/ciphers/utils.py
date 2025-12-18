from django.utils import timezone

from ciphers.models import CipherDayHistory


def get_today_cipher():
    obj = (
        CipherDayHistory.objects.select_related('cipher')
        .filter(date=timezone.localdate())
        .first()
    )
    return obj.cipher if obj else None
