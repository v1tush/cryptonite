from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    xp = models.PositiveIntegerField(default=0)
    email = models.EmailField(unique=True, verbose_name='email address')
    avatar = models.ImageField(
        upload_to='uploads/users/avatars/',
        null=True,
        blank=True,
        max_length=255,
    )
    background = models.ImageField(
        upload_to='uploads/users/backgrounds/',
        null=True,
        blank=True,
        max_length=255,
    )
    strike = models.PositiveIntegerField(default=0)
    money = models.PositiveIntegerField(default=0)

    @property
    def level(self):
        if self.xp < 100:
            return 1

        if self.xp < 300:
            return 2

        if self.xp < 600:
            return 3

        return 4
