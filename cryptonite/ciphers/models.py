from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Cipher(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, 'Middle'),
        (3, 'Hard'),
        (4, 'Hardcore'),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ciphers',
    )
    title = models.CharField(max_length=100)
    encrypted_phrase = models.CharField(max_length=100)
    answer_phrase = models.CharField(max_length=100)
    description = models.TextField(max_length=510)
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES)
    attempt_limit = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']


class CipherHelp(models.Model):
    cipher = models.ForeignKey(
        Cipher,
        on_delete=models.CASCADE,
        related_name='hints',
    )
    text = models.TextField()
    order = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.order is None:
            last = (
                CipherHelp.objects.filter(cipher=self.cipher)
                .order_by('-order')
                .first()
            )
            self.order = (last.order + 1) if last else 1

        super().save(*args, **kwargs)


class CipherComment(models.Model):
    cipher = models.ForeignKey(
        Cipher,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
