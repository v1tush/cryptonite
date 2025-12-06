from django.db.models.signals import post_save
from django.dispatch import receiver

from achievements.models import UserAchievement


@receiver(post_save, sender=UserAchievement)
def add_xp_for_achievement(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user

    user.xp += instance.achievement.xp_reward
    user.save(update_fields=['xp'])
