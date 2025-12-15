from django.db import models


class SolutionLogManager(models.Manager):
    def all_solutions_for_cipher(self, cipher):
        return self.filter(cipher=cipher)

    def user_solutions_for_cipher(self, user, cipher):
        return self.filter(user=user, cipher=cipher).order_by('-created_at')

    def has_attempts(self, user, cipher):
        return self.user_solutions_for_cipher(user, cipher).exists()

    def get_success_attempt(self, user, cipher):
        return (
            self.user_solutions_for_cipher(user, cipher)
            .filter(correct=True)
            .first()
        )

    def get_last_attempt(self, user, cipher):
        return self.user_solutions_for_cipher(user, cipher).first()

    def get_solved_users_cnt(self, cipher):
        return (
            self.all_solutions_for_cipher(cipher).filter(correct=True).count()
        )

    def get_top_solvers(self, cipher, limit=3):
        queryset = (
            self.filter(cipher=cipher, correct=True)
            .select_related('user')
            .values(
                'user__id',
                'user__username',
                'user__avatar',
            )
        )
        return queryset.annotate(
            min_attempts=models.Min('attempts_used'),
            first_solved=models.Min('created_at'),
        ).order_by('min_attempts', 'first_solved')[:limit]
