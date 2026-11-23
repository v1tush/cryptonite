import django.forms


# ! Вынесение виджетов формы в отдельный класс
class FormInitMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

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
