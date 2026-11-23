from io import BytesIO
from uuid import uuid4

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageOps


class ProfileImageField(forms.FileField):
    formats = {
        'JPEG': ('.jpg', 'image/jpeg'),
        'PNG': ('.png', 'image/png'),
    }

    def __init__(self, *, max_mb, max_side, **kwargs):
        self.max_mb = max_mb
        self.max_side = max_side
        kwargs.setdefault('required', False)
        kwargs.setdefault(
            'widget',
            forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png'}),
        )
        super().__init__(**kwargs)

    def to_python(self, data):
        upload = super().to_python(data)
        if upload is None:
            return None

        max_bytes = self.max_mb * 1024 * 1024
        if upload.size > max_bytes:
            raise forms.ValidationError(
                f'Файл слишком большой. Максимум {self.max_mb} МБ.',
                code='file_too_large',
            )

        try:
            with Image.open(upload, formats=list(self.formats)) as image:
                image_format = image.format
                if max(image.size) > self.max_side:
                    raise forms.ValidationError(
                        f'Максимальный размер стороны: {self.max_side} пикселей.',
                        code='image_too_large',
                    )
                if getattr(image, 'is_animated', False):
                    raise forms.ValidationError(
                        'Анимированные изображения не поддерживаются.',
                        code='animated_image',
                    )
                corrected = ImageOps.exif_transpose(image)
                with corrected.convert(
                    'RGB' if image_format == 'JPEG' else 'RGBA'
                ) as pixels:
                    # Encode only pixels: discard metadata and trailing data.
                    pixels.info.clear()
                    with BytesIO() as output:
                        pixels.save(output, format=image_format)
                        encoded = output.getvalue()
        except (
            OSError,
            ValueError,
            SyntaxError,
            Image.DecompressionBombError,
        ) as exc:
            raise forms.ValidationError(
                'Загрузите корректное изображение JPEG или PNG.',
                code='invalid_image',
            ) from exc

        if len(encoded) > max_bytes:
            raise forms.ValidationError(
                f'Изображение после обработки превышает {self.max_mb} МБ.',
                code='file_too_large',
            )
        extension, content_type = self.formats[image_format]
        return SimpleUploadedFile(
            f'{uuid4().hex}{extension}', encoded, content_type
        )
