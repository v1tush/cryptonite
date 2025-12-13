from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from django.db.models.signals import post_save

        import logs.models
        import users.signals

        post_save.connect(
            users.signals.update_solved_count,
            sender=logs.models.SolutionLog,
        )
