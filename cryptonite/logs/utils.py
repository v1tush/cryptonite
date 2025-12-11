from django.db import transaction
from django.db.models import F

from achievements.models import Achievement, UserAchievement


def grant_achievement(user, achievement_code):
    try:
        achievement = Achievement.objects.get(title=achievement_code)
    except Achievement.DoesNotExist:
        return

    if UserAchievement.objects.filter(
        user=user,
        achievement=achievement,
    ).exists():
        return

    with transaction.atomic():
        UserAchievement.objects.create(user=user, achievement=achievement)

        if achievement.xp_reward:
            user.xp = F('xp') + achievement.xp_reward
            user.save(update_fields=['xp'])


def check_achievements_for_log(log):
    user = log.user

    if log.correct:
        correct_logs = user.solution_logs.filter(correct=True)
        solved_count = correct_logs.values('cipher').distinct().count()
        if solved_count == 1:
            grant_achievement(user, 'Первый шаг')

    if log.correct and solved_count == 10:
        grant_achievement(user, 'Охотник за шифрами')

    if log.correct and log.attempts_used == 1:
        grant_achievement(user, 'Снайпер')

    last_logs = user.solution_logs.order_by('-id')[:5].values_list(
        'correct',
        flat=True,
    )
    if all(last_logs) and len(last_logs) == 5:
        grant_achievement(user, 'Серия побед')
