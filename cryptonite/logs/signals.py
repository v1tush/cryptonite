from django.db import transaction

from achievements.utils import collect_achievements_for_user


def update_achievements_on_log(sender, instance, created, **kwargs):
    if not created:
        return

    transaction.on_commit(
        lambda: collect_achievements_for_user(instance.user),
    )
