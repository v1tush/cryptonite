from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from ciphers.managers import CipherLikeManager, CipherManager
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
    description_for_moderator = models.TextField(max_length=510, verbose_name='описание для модератора')
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
        verbose_name = 'шифр'
        verbose_name_plural = 'шифры'

    def __str__(self):
        return f'Cipher: {self.author.username} - {self.title[:10]}'

    def clean(self):
        if self.cipher_type == 'course' and not self.course:
            raise ValidationError('Шифр курса должен быть привязан к курсу')

        if self.cipher_type == 'community' and self.course:
            raise ValidationError('Шифр сообщества не должен иметь курс')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'ciphers:solve_cipher',
            kwargs={'cipher_id': self.id},
        )

    @property
    def is_published(self):
        return self.status == 'approved'


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

    class Meta:
        verbose_name = 'подсказка к шифру'
        verbose_name_plural = 'подсказки к шифрам'

    def __str__(self):
        return f'CipherHelp: {self.cipher.title} - {self.order}'

    def save(self, *args, **kwargs):
        if self.order is None:
            last = (
                CipherHelp.objects.filter(cipher=self.cipher)
                .order_by('-order')
                .first()
            )
            self.order = (last.order + 1) if last else 1

        super().save(*args, **kwargs)


class PurchasedHint(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchased_hints',
        verbose_name='пользователь',
    )
    hint = models.ForeignKey(
        CipherHelp,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='подсказка',
    )
    purchased_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата покупки',
    )

    class Meta:
        verbose_name = 'купленная подсказка'
        verbose_name_plural = 'купленные подсказки'
        unique_together = ['user', 'hint']

    def __str__(self):
        return (
            'PurchasedHint: '
            f'{self.user.username}'
            f' → {self.hint.cipher.title} (подсказка {self.hint.order})'
        )


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

    class Meta:
        verbose_name = 'комментарий к шифру'
        verbose_name_plural = 'комментарии к шифрам'

    def __str__(self):
        return (
            f'CipherComment: {self.user.username} - {self.cipher.title[:10]}'
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
        verbose_name = 'история шифров дня'
        verbose_name_plural = 'истории шифров дня'
        constraints = [
            models.UniqueConstraint(
                fields=['date'],
                name='unique_cipher_day',
            ),
        ]

    def __str__(self):
        return f'CipherDayHistory: {self.cipher.title} - {self.date}'


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
        verbose_name = 'лайк шифра'
        verbose_name_plural = 'лайки шифров'

    def __str__(self):
        return f'CipherLike: {self.user.username} - {self.created_at}'


class CipherExample(models.Model):
    cipher = models.ForeignKey(Cipher, models.CASCADE, related_name='examples')

    encrypted_phrase = models.CharField(
        max_length=100,
        verbose_name='пример зашифрованной фразы',
    )
    answer_phrase = models.CharField(max_length=100, verbose_name='ответ на пример')

    order = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='порядок',
    )
