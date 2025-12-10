from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Exists, OuterRef


User = get_user_model()


class CipherManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(likes_count=Count('likes'))

    def with_user_likes(self, user):
        from ciphers.models import CipherLike

        return self.get_queryset().annotate(
            liked_by_user=Exists(
                CipherLike.objects.filter(user=user, cipher=OuterRef('pk')),
            ),
        )

    def approved(self):
        return self.get_queryset().filter(status='approved')

    def with_user_likes_and_approved(self, user):
        return self.with_user_likes(user).filter(status='approved')


class CipherLikeManager(models.Manager):
    def cipher_count_likes(self, cipher):
        return self.get_queryset().filter(cipher=cipher).count()
