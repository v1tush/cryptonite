from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm, UserChangeForm
from django.utils.html import format_html

from users.fields import ProfileImageField
from users.models import CustomUser


class ProfileAdminForm(UserChangeForm):
    avatar = ProfileImageField(max_mb=2, max_side=2048)
    background = ProfileImageField(max_mb=5, max_side=4096)

    class Meta(UserChangeForm.Meta):
        model = CustomUser


class AdminPasswordOnlyForm(AdminPasswordChangeForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save(update_fields=['password'])
        return user


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    form = ProfileAdminForm
    change_password_form = AdminPasswordOnlyForm

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
        'xp',
        'money',
        'solved_ciphers_count',
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

    def save_model(self, request, obj, form, change):
        if not change:
            return super().save_model(request, obj, form, change)
        changes = set(form.changed_data)
        fields = [
            field.name
            for field in obj._meta.concrete_fields
            if field.name in changes
        ]
        if fields:
            obj.save(update_fields=fields)

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
