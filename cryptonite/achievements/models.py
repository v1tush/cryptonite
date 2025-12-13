from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Achievement(models.Model):
    title = models.CharField(max_length=100, verbose_name='название')
    description = models.TextField(max_length=500, verbose_name='описание')
    image = models.ImageField(
        upload_to='uploads/achievements/',
        null=True,
        blank=True,
        verbose_name='изображение',
    )
    xp_reward = models.PositiveIntegerField(
        default=0,
        verbose_name='количество опыта для достижения',
    )

    class Meta:
        verbose_name = 'достижение'
        verbose_name_plural = 'достижения'

    def __str__(self):
        return f'{self.title[:15]} {self.xp_reward}'


class UserAchievement(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='пользователь',
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        verbose_name='достижение',
    )
    achieved_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата получения',
    )

    class Meta:
        verbose_name = 'достижение пользователя'
        verbose_name_plural = 'достижения пользователей'
        #  чтобы 1 пользователь не мог получить
        # одно и то же достижение несколько раз
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f'{self.user.username} - {self.achievement.title}'
