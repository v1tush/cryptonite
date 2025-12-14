import datetime

from django.db import transaction

import ciphers.models


def setting_daily_cipher():
    today = datetime.date.today()

    if ciphers.models.CipherDayHistory.objects.filter(
        date=today,
    ).exists():
        return

    with transaction.atomic():
        available_ciphers = ciphers.models.Cipher.objects.filter(
            status='approved',
        ).exclude(
            id__in=ciphers.models.CipherDayHistory.objects.values_list(
                'cipher_id',
                flat=True,
            ),
        )

        if not available_ciphers.exists():
            ciphers.models.CipherDayHistory.objects.all().delete()

            available_ciphers = ciphers.models.Cipher.objects.filter(
                status='approved',
            )

        # Если база данных пуста
        if not available_ciphers.exists():
            return

        cipher = available_ciphers.order_by('?').first()

        ciphers.models.CipherDayHistory.objects.create(
            cipher=cipher,
            date=today,
        )
