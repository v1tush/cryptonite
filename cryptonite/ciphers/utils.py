from datetime import date

from ciphers.models import CipherDayHistory


def get_today_cipher():
    obj = (
        CipherDayHistory.objects.select_related('cipher')
        .filter(date=date.today())
        .first()
    )
    return obj.cipher if obj else None
