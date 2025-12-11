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
