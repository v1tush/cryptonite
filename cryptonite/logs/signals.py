from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


from logs.models import SolutionLog
from logs.utils import check_achievements_for_log


# ! TODO: Проверить сигнал на рвботоспособность
# Юля: ААААААА я даже не смогла решить задачу:
# AttributeError: 'Cipher' object has no attribute 'solved_ciphers_count'
@receiver(post_save, sender=SolutionLog)
def update_solved_ciphers_count(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.correct:
        return

    user = instance.user
    cipher = instance.cipher
    cipher.solved_ciphers_count += 1
    cipher.save()

    with transaction.atomic():
        already_solved = (
            SolutionLog.objects.filter(user=user, cipher=cipher, correct=True)
            .exclude(pk=instance.pk)
            .exists()
        )

        if not already_solved:
            user.solved_ciphers_count += 1
            user.save(update_fields=['solved_ciphers_count'])


@receiver(post_save, sender=SolutionLog)
def achievements_from_logs(sender, instance, created, **kwargs):
    if not created:
        return

    check_achievements_for_log(instance)
