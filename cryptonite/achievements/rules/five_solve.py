from achievements.rules.base import AchievementAbstract
from logs.models import SolutionLog


class FiveSolvesRule(AchievementAbstract):
    code = 'five_solves'

    def is_achieved(self, user):
        return (
            SolutionLog.objects.filter(
                user=user,
                correct=True,
            ).count()
            >= 5
        )
