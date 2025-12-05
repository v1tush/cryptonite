from django.contrib.auth.models import AbstractUser
from django.db import models


# TODO: Витялия, поправь модельку, писал в тг ;)
class CustomUser(AbstractUser):
    xp = models.PositiveIntegerField(default=0)

    avatar = models.ImageField(
        upload_to='uploads/users/avatars/',
        null=True,
        blank=True,
    )

    email = models.EmailField(
        blank=False,
        null=False,
        unique=True,
    )

    background = models.ImageField(
        upload_to='uploads/users/backgrounds/',
        null=True,
        blank=True,
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
