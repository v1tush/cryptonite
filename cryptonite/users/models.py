from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username


class CustomUser(AbstractUser):
    xp = models.PositiveIntegerField(default=0, verbose_name='опыт')
    username = models.CharField(
        max_length=32,
        unique=True,
        validators=[validate_username],
        verbose_name='имя пользователя',
    )
    email = models.EmailField(unique=True, verbose_name='email address')
    about_me = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='о себе',
    )
    avatar = models.ImageField(
        upload_to='uploads/users/avatars/',
        null=True,
        blank=True,
        max_length=255,
        verbose_name='аватар',
    )
    background = models.ImageField(
        upload_to='uploads/users/backgrounds/',
        null=True,
        blank=True,
        max_length=255,
        verbose_name='фон',
    )
    strike = models.PositiveIntegerField(default=0, verbose_name='страйки')
    money = models.PositiveIntegerField(default=0, verbose_name='деньги')
    solved_ciphers_count = models.PositiveIntegerField(
        default=0,
        verbose_name='количество решённых шифров',
    )

    @property
    def level(self):
        if self.xp < 100:
            return 1

        if self.xp < 300:
            return 2

        if self.xp < 600:
            return 3

        return 4
