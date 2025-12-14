from django.db import models
from django.db.models import Count, Exists, OuterRef, Q


class CipherQuerySet(models.QuerySet):
    def approved(self):
        return (
            self.filter(status='approved')
            .select_related('author')
            .prefetch_related('likes')
            .annotate(
                likes_count=Count('likes', distinct=True),
                correct_solutions_count=Count(
                    'solution_logs',
                    filter=Q(solution_logs__correct=True),
                    distinct=True,
                ),
            )
        )

    def with_user_likes_and_solutions(self, user):
        from ciphers.models import CipherLike
        from logs.models import SolutionLog

        return self.annotate(
            liked_by_user=Exists(
                CipherLike.objects.filter(user=user, cipher=OuterRef('pk')),
            ),
            solved_by_user=Exists(
                SolutionLog.objects.filter(
                    user=user, cipher=OuterRef('pk'), correct=True,
                ),
            ),
        )
