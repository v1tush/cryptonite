from django.apps import AppConfig


class LogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logs'

    # def ready(self):
    #     from django.db.models.signals import post_save

    #     import logs.signals
    #     import logs.models

    #     post_save.connect(
    #         logs.signals.update_solved_ciphers_count,
    #         sender=logs.models.SolutionLog,
    #     )

    #     post_save.connect(
    #         logs.signals.achievements_from_logs,
    #         sender=logs.models.SolutionLog,
    #     )
