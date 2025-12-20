from django.db import models
from django.db.models import Count, Exists, OuterRef, Prefetch, Q


class CipherQuerySet(models.QuerySet):
    def with_stats(self):
        return (
            self.select_related('author')
            .prefetch_related('likes', 'hints')
            .annotate(
                likes_count=Count('likes', distinct=True),
                correct_solutions_count=Count(
                    'solution_logs__user',
                    filter=Q(solution_logs__correct=True),
                    distinct=True,
                ),
            )
        )

    def with_full_data(self):
        return self.select_related('author', 'course').prefetch_related('hints', 'examples')

    def approved(self):
        return self.filter(status='approved').with_stats()

    def pending(self):
        return self.filter(status='pending').with_stats()

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
        from logs.models import SolutionLog

        return self.filter(
            solution_logs__user=user,
            solution_logs__correct=True,
        ).prefetch_related(
            Prefetch(
                'solution_logs',
                queryset=SolutionLog.objects.filter(user=user, correct=True),
                to_attr='user_solved_logs',
            ),
        )

    def get_some_most_popular_ciphers(self, num):
        return self.approved().order_by('-correct_solutions_count')[:num]
