from django.db import models

from users.models import CustomUser


def get_user_ranking_position(user):
    higher_ranked_count = CustomUser.objects.filter(
        models.Q(xp__gt=user.xp)
        | models.Q(xp=user.xp, date_joined__lt=user.date_joined),
    ).count()

    return higher_ranked_count + 1
