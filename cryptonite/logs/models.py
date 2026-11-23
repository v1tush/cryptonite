from django.contrib.auth import get_user_model
from django.db import models

from ciphers.models import Cipher
from logs.managers import SolutionLogManager

User = get_user_model()


class SolutionLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solution_logs',
        verbose_name='пользователь',
    )
    cipher = models.ForeignKey(
        Cipher,
        on_delete=models.CASCADE,
        related_name='solution_logs',
        verbose_name='шифр',
    )
    correct = models.BooleanField(verbose_name='правильный ответ')
    attempted_answer = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='текст попытки ответа',
    )
    attempts_used = models.PositiveIntegerField(
        default=1,
        verbose_name='использованные попытки',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )
    score = models.PositiveIntegerField(
        default=0,
        verbose_name='балл',
    )

    objects = SolutionLogManager()

    class Meta:
        verbose_name = 'лог решения'
        verbose_name_plural = 'логи решений'

        constraints = [
            models.UniqueConstraint(
                fields=['cipher', 'user', 'attempts_used'],
                name='unique_cipher_solution_per_user',
            ),
        ]

    def __str__(self):
        return f'SolutionLog: {self.user} - {self.cipher}'

    @property
    def is_solved(self):
        return self.correct
