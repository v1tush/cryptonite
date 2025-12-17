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
    django.forms.ModelForm,
):
    class Meta:
        model = User
        fields = (
            'about_me',
            'username',
            'email',
            'about_me',
            'avatar',
            'background',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username).exclude(
            pk=self.instance.pk,
        )

        if qs.exists():
            raise django.forms.ValidationError(
                'Пользователь с таким ником уже существует.',
            )

        return username
