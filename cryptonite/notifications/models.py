from django.db import models

import users.models


class NotificationModel(models.Model):
    class StatusChoices(models.TextChoices):
        UNREAD = 'unread', 'непрочитано'
        READ = 'read', 'прочитано'

    class StatusChoicesClassification(models.TextChoices):
        INFO = 'info', 'информационное'
        LIKING = 'liking', 'лайк'
        COMMENT = 'comment', 'комментарий'
        SYSTEM = 'system', 'системное'

    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.UNREAD,
        verbose_name='статус уведомления',
        db_index=True,
    )

    classification = models.CharField(
        max_length=15,
        choices=StatusChoicesClassification.choices,
        default=StatusChoicesClassification.INFO,
        verbose_name='классификация уведомления',
        db_index=True,
    )

    created_on = models.DateTimeField(
        auto_now_add=True,
        null=True,
        verbose_name='дата и время создания',
        db_index=True,
    )

    text = models.TextField(
        verbose_name='текст уведомления',
        help_text='текст уведомления для пользователя',
        blank=True,
    )

    # для кого уведомление
    user = models.ForeignKey(
        users.models.CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='пользователь',
    )

    class Meta:
        verbose_name = 'уведомление'
        verbose_name_plural = 'уведомления'

    def __str__(self):
        return f'{self.get_classification_display()} → {self.user.username}'
