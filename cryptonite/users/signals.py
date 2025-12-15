from django.db.models import F

from logs.models import SolutionLog


def update_solved_count(sender, instance, created, **kwargs):
    if created and instance.correct:
        user = instance.user
        cipher = instance.cipher

        already_solved = (
            SolutionLog.objects.filter(user=user, cipher=cipher, correct=True)
            .exclude(pk=instance.pk)
            .exists()
        )

        if not already_solved:
            user.solved_ciphers_count = F('solved_ciphers_count') + 1
            user.save(update_fields=['solved_ciphers_count'])
