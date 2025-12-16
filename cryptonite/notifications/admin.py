from django.contrib import admin

from notifications.models import NotificationModel


@admin.register(NotificationModel)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'classification',
        'status',
        'short_text',
        'created_on',
    )

    list_filter = (
        'status',
        'classification',
        'created_on',
    )

    search_fields = (
        'text',
        'user__username',
        'user__email',
    )

    ordering = ('-created_on',)

    list_select_related = ('user',)

    readonly_fields = ('created_on',)

    fieldsets = (
        (
            None,
            {
                'fields': ('user', 'classification', 'status'),
            },
        ),
        (
            'Содержимое',
            {
                'fields': ('text',),
            },
        ),
        (
            'Системная информация',
            {
                'fields': ('created_on',),
            },
        ),
    )

    @admin.display(description='Текст')
    def short_text(self, obj):
        if not obj.text:
            return '—'

        return obj.text[:50] + ('…' if len(obj.text) > 50 else '')
