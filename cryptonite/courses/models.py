from django.db import models

from users.models import CustomUser


class Course(models.Model):
    title = models.CharField(max_length=100, verbose_name='название')
    description = models.TextField(max_length=510, verbose_name='описание')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='course',
        verbose_name='автор',
    )

    class Meta:
        verbose_name = 'курс'
        verbose_name_plural = 'курсы'

    def __str__(self):
        return f'Course: {self.title[:15]} - {self.author.username}'
