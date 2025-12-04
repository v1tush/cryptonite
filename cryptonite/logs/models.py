from django.contrib.auth import get_user_model
from django.db import models

from ciphers.models import Cipher


User = get_user_model()


class SolutionLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solution_logs',
    )
    cipher = models.ForeignKey(
        Cipher,
        on_delete=models.CASCADE,
        related_name='solution_logs',
    )
    correct = models.BooleanField()
    attempted_answer = models.CharField(max_length=100, null=True, blank=True)
    attempts_used = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.attempts_used:
            last_attempt = (
                SolutionLog.objects.filter(user=self.user, cipher=self.cipher)
                .order_by('-attempts_used')
                .first()
            )
            self.attempts_used = (
                (last_attempt.attempts_used + 1) if last_attempt else 1
            )

        super().save(*args, **kwargs)
