from django.contrib import admin

from achievements.models import Achievement, UserAchievement


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'code',
        'title',
        'xp_reward',
    )
    list_display_links = (
        'id',
        'code',
        'title',
    )
    search_fields = (
        'title',
        'code',
        'description',
    )
    list_filter = ('xp_reward',)
    ordering = (
        'xp_reward',
        'title',
    )
    fields = (
        'title',
        'code',
        'description',
        'image',
        'xp_reward',
    )


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'achievement',
        'achieved_at',
    )
    list_display_links = ('id',)
    search_fields = (
        'user__username',
        'achievement__title',
    )
    list_filter = (
        'achievement',
        'achieved_at',
    )
    ordering = ('-achieved_at',)
    autocomplete_fields = (
        'user',
        'achievement',
    )
