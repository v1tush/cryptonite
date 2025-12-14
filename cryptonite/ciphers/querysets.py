from django.db import models
from django.db.models import Count, Exists, OuterRef, Q


class CipherQuerySet(models.QuerySet):
    def all(self):
        return (
            self.select_related('author')
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

    def approved(self):
        return self.all().filter(status='approved')

    def with_user_likes_and_solutions(self, user):
        from ciphers.models import CipherLike
        from logs.models import SolutionLog

        return self.annotate(
            liked_by_user=Exists(
                CipherLike.objects.filter(user=user, cipher=OuterRef('pk')),
            ),
            solved_by_user=Exists(
                SolutionLog.objects.filter(
                    user=user,
                    cipher=OuterRef('pk'),
                    correct=True,
                ),
            ),
        )

    def get_all_user_solved_ciphers(self, user):
        return self.filter(
            solution_logs__user=user,
            solution_logs__correct=True,
        )

    def get_some_most_popular_ciphers(self, num):
        return self.approved().order_by('-correct_solutions_count')[:num]
