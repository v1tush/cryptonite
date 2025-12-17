from django.db import models

from ciphers.models import Cipher
from qr.managers import QrManager


class QR(models.Model):
    cipher = models.OneToOneField(
        Cipher,
        on_delete=models.CASCADE,
        related_name='qr_code',
        verbose_name='шифр',
    )

    image = models.ImageField(
        upload_to='qr_codes/',
        verbose_name='изображение QR-кода',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )

    objects = QrManager()

    class Meta:
        verbose_name = 'QR-код'
        verbose_name_plural = 'QR-коды'

    def __str__(self):
        return f'QR: {self.cipher.title}'
