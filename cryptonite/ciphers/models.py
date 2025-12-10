from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from courses.models import Course
from ciphers.managers import CipherManager, CipherLikeManager

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
        ('hidden', 'Скрыт'),
    ]
    CIPHER_TYPES = [
        ('course', 'Курс'),
        ('community', 'Сообщество'),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ciphers',
        verbose_name='автор',
    )
    title = models.CharField(max_length=100, verbose_name='название')
    encrypted_phrase = models.CharField(
        max_length=100,
        verbose_name='зашифрованная фраза',
    )
    answer_phrase = models.CharField(max_length=100, verbose_name='ответ')
    description = models.TextField(max_length=510, verbose_name='описание')
    difficulty = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_CHOICES,
        verbose_name='сложность',
    )
    attempt_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='лимит попыток',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='дата обновления',
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='опубликован',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='статус',
    )
    cipher_type = models.CharField(
        max_length=10,
        choices=CIPHER_TYPES,
        default='community',
        verbose_name='тип шифра',
    )
    course = models.ForeignKey(
        Course,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='курс',
    )

    objects = CipherManager()

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
        verbose_name='шифр',
    )
    text = models.TextField(verbose_name='текст подсказки')
    order = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='порядок',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='дата обновления',
    )

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
        verbose_name='шифр',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )
    text = models.TextField(verbose_name='текст комментария')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )


class CipherDayHistory(models.Model):
    cipher = models.ForeignKey(
        Cipher,
        on_delete=models.CASCADE,
        related_name='cipher_day_history',
        verbose_name='шифр',
    )
    date = models.DateField(verbose_name='дата')

    class Meta:
        ordering = ['date']


class CipherLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='пользователь',
    )
    cipher = models.ForeignKey(
        Cipher,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='шифр',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )

    objects = CipherLikeManager()

    class Meta:
        unique_together = ('user', 'cipher')
