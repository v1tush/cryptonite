from django.db import models

from ciphers.models import Cipher
import feedback.managers
from users.models import CustomUser


class Feedback(models.Model):
    STATUS_CHOICES = [
        ('received', 'получено'),
        ('in_progress', 'в обработке'),
        ('answered', 'ответ дан'),
    ]
    text = models.TextField(
        verbose_name='жалоба',
        help_text='Напишите здесь причину жалобы',
        blank=True,
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        null=True,
        verbose_name='дата и время создания',
    )
    status = models.CharField(
        choices=STATUS_CHOICES,
        default='received',
        verbose_name='статус обработки',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='feedback',
        verbose_name='Автор',
    )
    cipher = models.ForeignKey(
        Cipher,
        on_delete=models.CASCADE,
        related_name='feedback',
        verbose_name='Шифр',
    )

    objects = feedback.managers.FeedbackManager()

    class Meta:
        verbose_name = 'жалоба'
        verbose_name_plural = 'жалобы'

    def __str__(self):
        return f'Feedback: {self.text[:15]} - {self.author.username}'
