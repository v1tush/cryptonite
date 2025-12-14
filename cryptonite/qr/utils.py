from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.urls import reverse
import segno

from qr.models import QR


def create_qr_for_cipher(cipher):
    url = settings.SITE_URL + reverse(
        'ciphers:solve_cipher',
        kwargs={'cipher_id': cipher.pk},
    )

    if hasattr(cipher, 'qr_code') and cipher.qr_code.image:
        return cipher.qr_code

    qr = segno.make(
        url,
        micro=False,
        error='Q',
    )

    buffer = BytesIO()
    qr.save(
        buffer,
        kind='png',
        scale=8,
        border=2,
        dark='white',
        light=None,
    )

    qr_obj = QR(cipher=cipher)
    qr_obj.image.save(
        f'cipher_{cipher.pk}_qr.png',
        ContentFile(buffer.getvalue()),
        save=True,
    )

    return qr_obj
