from django.db.models.signals import post_save
from django.dispatch import receiver


from logs.models import SolutionLog
from logs.utils import check_achievements_for_log


@receiver(post_save, sender=SolutionLog)
def achievements_from_logs(sender, instance, created, **kwargs):
    if not created:
        return

    check_achievements_for_log(instance)
