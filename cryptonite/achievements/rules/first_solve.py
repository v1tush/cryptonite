from achievements.rules.base import AchievementAbstract
from logs.models import SolutionLog


class FirstSolveRule(AchievementAbstract):
    code = 'first_solve'

    def is_achieved(self, user):
        return SolutionLog.objects.filter(
            user=user,
            correct=True,
        ).exists()
