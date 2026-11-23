from django.contrib.auth import get_user_model
from django.db import models

from ciphers.querysets import CipherQuerySet

User = get_user_model()


class CipherManager(models.Manager):
    def get_queryset(self):
        return CipherQuerySet(self.model, using=self._db)

    def approved(self):
        return self.get_queryset().approved()

    def pending(self):
        return self.get_queryset().pending()

    def with_user_likes_and_solutions(self, user):
        return self.get_queryset().with_user_likes_and_solutions(user)

    def with_stats(self):
        return self.get_queryset().with_stats()

    def get_all_user_solved_ciphers(self, user):
        return self.get_queryset().get_all_user_solved_ciphers(user)

    def get_some_most_popular_ciphers(self, num):
        return self.get_queryset().get_some_most_popular_ciphers(num)


class CipherLikeManager(models.Manager):
    def cipher_count_likes(self, cipher):
        return self.get_queryset().filter(cipher=cipher).count()
