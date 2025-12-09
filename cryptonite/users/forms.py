import django.contrib.auth
import django.contrib.auth.forms
import django.forms

import core.forms
import users.models


User = django.contrib.auth.get_user_model()


# ! Форма регистрации
class UserCreationForm(
    core.forms.FormInitMixin,
    core.forms.CommonUserRowsMixin,
    django.contrib.auth.forms.UserCreationForm,
):
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
            'email',
            'avatar',
            'password1',
            'password2',
        )


class ProfileChangeForm(
    core.forms.FormInitMixin,
    core.forms.CommonUserRowsMixin,
    django.contrib.auth.forms.UserChangeForm,
):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'about_me',
            'avatar',
            'background',
        )
