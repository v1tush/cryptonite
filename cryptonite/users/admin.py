from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = (
        'id',
        'username',
        'email',
        'level_display',
        'xp',
        'money',
        'solved_ciphers_count',
        'is_staff',
        'is_active',
    )

    list_filter = (
        'is_staff',
        'is_active',
        'is_superuser',
    )

    search_fields = (
        'username',
        'email',
    )

    ordering = ('-xp',)

    readonly_fields = (
        'last_login',
        'date_joined',
        'level_display',
        'avatar_preview',
        'background_preview',
    )

    fieldsets = (
        (
            'Основная информация',
            {
                'fields': (
                    'username',
                    'email',
                    'password',
                ),
            },
        ),
        (
            'Профиль',
            {
                'fields': (
                    'about_me',
                    'avatar',
                    'avatar_preview',
                    'background',
                    'background_preview',
                ),
            },
        ),
        (
            'Прогресс',
            {
                'fields': (
                    'xp',
                    'level_display',
                    'money',
                    'solved_ciphers_count',
                    'strike',
                ),
            },
        ),
        (
            'Права доступа',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (
            'Системная информация',
            {
                'fields': (
                    'last_login',
                    'date_joined',
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'is_staff',
                    'is_active',
                ),
            },
        ),
    )

    def level_display(self, obj):
        return obj.level

    level_display.short_description = 'Уровень'
    level_display.admin_order_field = 'xp'

    def avatar_preview(self, obj):
        if obj.avatar and obj.avatar.storage.exists(obj.avatar.name):
            return format_html(
                '<img src="{}" style="max-height: 100px; '
                'border-radius: 8px;" />',
                obj.avatar.url,
            )

        return '—'

    avatar_preview.short_description = 'Аватар'

    def background_preview(self, obj):
        if obj.background and obj.background.storage.exists(
            obj.background.name,
        ):
            return format_html(
                '<img src="{}" style="max-height: 100px;'
                'border-radius: 8px;" />',
                obj.background.url,
            )

        return '—'

    background_preview.short_description = 'Фон'
