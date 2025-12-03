from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    xp = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(upload_to='uploads/users/avatars/', null=True, blank=True)
    background = models.ImageField(upload_to='uploads/users/backgrounds/', null=True, blank=True)
    strike = models.PositiveIntegerField(default=0)