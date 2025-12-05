import django.contrib.auth.forms
import django.core.exceptions
import django.forms
import PIL

import core.forms
import users.models


# ! Форма регистрации
class UserCreationForm(
    core.forms.FormInitMixin,
    django.contrib.auth.forms.UserCreationForm,
):
    # ! Добавление проверки на обязательное наличие поля и тд.
    username = django.forms.CharField(
        widget=django.forms.TextInput(
            attrs={
                'placeholder': 'Введите ваш @username',
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    first_name = django.forms.CharField(
        widget=django.forms.TextInput(
            attrs={
                'placeholder': 'Введите ваше имя',
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    last_name = django.forms.CharField(
        widget=django.forms.TextInput(
            attrs={
                'placeholder': 'Введите ваше фамилию',
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    email = django.forms.EmailField(
        widget=django.forms.EmailInput(
            attrs={
                'placeholder': 'Введите ваш email',
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    avatar = django.forms.ImageField(
        widget=django.forms.FileInput(
            attrs={
                'placeholder': 'Загрузите вашу аватарку',
            },
        ),
        required=False,
    )

    password1 = django.forms.CharField(
        widget=django.forms.PasswordInput(
            attrs={
                'placeholder': 'Введите пароль',
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    password2 = django.forms.CharField(
        widget=django.forms.PasswordInput(
            attrs={
                'placeholder': 'Подтвердите пароль',
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    class Meta:
        model = users.models.CustomUser

        # * Поля формы для CustomUser (users/models.py/CustomUser)
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'avatar',
            'password1',
            'password2',
        )

    def clean_avatar(self):  # ** Валидация входящего изображения
        avatar = self.cleaned_data.get('avatar')

        if avatar:
            # * Проверка веса изображения
            if avatar.size > 2 * 1024 * 1024:
                raise django.core.exceptions.ValidationError(
                    'Файл слишком большой. Максимум 2 МБ.',
                )

            if avatar.content_type not in ['image/jpeg', 'image/png']:
                raise django.core.exceptions.ValidationError(
                    'Разрешены только форматы JPEG и PNG.',
                )

            try:
                with PIL.Image.open(avatar) as img:
                    max_width, max_height = 400, 400

                    # * Проверки разрешения изображений
                    if img.width > max_width or img.height > max_height:
                        raise django.core.exceptions.ValidationError(
                            'Изображение слишком большое',
                        )

                    if img.width < 300 or img.height < 300:
                        raise django.core.exceptions.ValidationError(
                            'Изображение слишком маленькое',
                        )

            except PIL.UnidentifiedImageError:
                raise django.core.exceptions.ValidationError(
                    'Файл не является изображением или с ним что-то не так',
                )

        return avatar

    def clean_email(self):  # * небольшая нормальзация email
        email = self.cleaned_data.get('email')

        local, _, domain = email.partition('@')
        local = local.split('+')[0]

        return f'{local}@{domain}'
