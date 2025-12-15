from django.db import transaction

from achievements.models import Achievement, UserAchievement
from achievements.rules.utils import get_rules


def collect_achievements_for_user(user):
    achievements_map = {a.code: a for a in Achievement.objects.all()}

    user_codes = set(
        UserAchievement.objects.filter(user=user).values_list(
            'achievement__code', flat=True,
        ),
    )

    new_links = [
        UserAchievement(user=user, achievement=achievement)
        for rule in get_rules()
        if rule.code not in user_codes
        if (achievement := achievements_map.get(rule.code))
        if rule.is_achieved(user)
    ]

    if new_links:
        with transaction.atomic():
            UserAchievement.objects.bulk_create(
                new_links,
                ignore_conflicts=True,
            )
