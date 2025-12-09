from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=100, verbose_name='название')
    description = models.TextField(max_length=510, verbose_name='описание')
