import re

from django.core.exceptions import ValidationError


def validate_username(username):
    if not re.fullmatch(r'[A-Za-z]\w{4,31}', username):
        raise ValidationError(
            (
                'Имя пользователя должно начинаться с латинской буквы и '
                'содержать только латинские буквы, цифры и знак подчеркивания,'
                ' длина от 5 до 32 символов.'
            ),
            code='invalid_chars',
        )

    return username
