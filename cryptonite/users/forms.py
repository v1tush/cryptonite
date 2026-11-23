import django.contrib.auth
import django.contrib.auth.forms
import django.forms

import core.forms
import users.models
from users.fields import ProfileImageField

User = django.contrib.auth.get_user_model()


# ! Форма регистрации
class UserCreationForm(
    core.forms.FormInitMixin,
    core.forms.CommonUserRowsMixin,
    django.contrib.auth.forms.UserCreationForm,
):
    avatar = ProfileImageField(max_mb=2, max_side=2048)

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
    avatar = ProfileImageField(max_mb=2, max_side=2048)
    background = ProfileImageField(max_mb=5, max_side=4096)

    class Meta:
        model = User
        fields = (
            'about_me',
            'username',
            'email',
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


class SavePasswordOnlyMixin:
    def set_password_and_save(
        self, user, password_field_name='password1', commit=True
    ):
        user.set_password(self.cleaned_data[password_field_name])
        if commit:
            user.save(update_fields=['password'])
        return user


class PasswordChangeForm(
    SavePasswordOnlyMixin,
    django.contrib.auth.forms.PasswordChangeForm,
):
    pass


class SetPasswordForm(
    SavePasswordOnlyMixin,
    django.contrib.auth.forms.SetPasswordForm,
):
    pass
