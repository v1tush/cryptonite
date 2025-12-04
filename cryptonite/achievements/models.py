from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Achievement(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    image = models.ImageField(
        upload_to='uploads/achievements/',
        null=True,
        blank=True,
    )
    xp_reward = models.PositiveIntegerField(default=0)


class UserAchievement(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements',
    )
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    achieved_at = models.DateTimeField(auto_now_add=True)
