from django.db import models

from ciphers.models import Cipher


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

    def __str__(self):
        return f'QR: {self.cipher.title}'
