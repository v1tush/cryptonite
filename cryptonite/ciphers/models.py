from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from courses.models import Course

User = get_user_model()


class Cipher(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, 'Middle'),
        (3, 'Hard'),
        (4, 'Hardcore'),
    ]
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Принят'),
        ('rejected', 'Отклонён'),
    ]
    CIPHER_TYPES = [
        ('course', 'Курс'),
        ('community', 'Сообщество'),
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
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
    )
    cipher_type = models.CharField(max_length=10, choices=CIPHER_TYPES)
    course = models.ForeignKey(
        Course,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.cipher_type == 'course' and not self.course:
            raise ValidationError('Шифр курса должен быть привязан к курсу')

        if self.cipher_type == 'community' and self.course:
            raise ValidationError('Шифр сообщества не должен иметь курс')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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


class CipherDayHistory(models.Model):
    cipher = models.ForeignKey(Cipher, on_delete=models.CASCADE)
    date = models.DateField()


class CipherLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cipher = models.ForeignKey(Cipher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'cipher')
