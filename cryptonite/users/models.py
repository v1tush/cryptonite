from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import LEVEL_THRESHOLDS
from users.validators import validate_username


class CustomUser(AbstractUser):
    xp = models.PositiveIntegerField(default=0, verbose_name='опыт')
    username = models.CharField(
        max_length=32,
        unique=True,
        validators=[validate_username],
        verbose_name='имя пользователя',
    )
    email = models.EmailField(unique=True, verbose_name='электронная почта')
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

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return f'CustomUser: {self.username} ({self.email})'

    @property
    def level(self):
        for lvl, xp_required in reversed(LEVEL_THRESHOLDS):
            if self.xp >= xp_required:
                return lvl

        return 1
