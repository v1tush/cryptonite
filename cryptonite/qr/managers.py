from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
import segno


class QrManager(models.Manager):
    def _create_qr_photo(self, url: str) -> ContentFile:
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
        )

        buffer.seek(0)

        return ContentFile(
            buffer.read(),
        )

    def create_qr_for_cipher(self, cipher, request):
        from qr.models import QR

        qr_obj, created = QR.objects.get_or_create(cipher=cipher)

        if created:
            url = request.build_absolute_uri(
                cipher.get_absolute_url(),
            )

            qr_obj.image.save(
                f'cipher_{cipher.id}_qr.png',
                self._create_qr_photo(url),
                save=True,
            )

        return qr_obj
