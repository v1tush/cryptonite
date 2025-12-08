import django.core.exceptions


# ! Вынесение виджетов формы в отдельный класс
class FormInitMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

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

        return avatar

    def clean_email(self):  # * небольшая нормальзация email
        email = self.cleaned_data.get('email')

        local, _, domain = email.partition('@')
        local = local.split('+')[0]

        return f'{local}@{domain}'


# ! Вынесение повторяющихся полей
class CommonUserRowsMixin:
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
