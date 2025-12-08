from django.apps import AppConfig


class AchievementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'achievements'

    def ready(self):
        from django.db.models.signals import post_save

        import achievements.signals
        import achievements.models

        post_save.connect(
            achievements.signals.add_xp_for_achievement,
            sender=achievements.models.UserAchievement,
        )
