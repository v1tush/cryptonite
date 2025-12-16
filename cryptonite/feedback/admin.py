from django.contrib import admin

from feedback.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'cipher',
        'status',
        'created_on',
    )

    list_filter = (
        'status',
        'created_on',
    )

    search_fields = (
        'text',
        'author__username',
        'cipher__title',
    )

    list_select_related = (
        'author',
        'cipher',
    )

    ordering = ('-created_on',)

    readonly_fields = (
        'author',
        'cipher',
        'created_on',
    )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'author',
                    'cipher',
                    'text',
                ),
            },
        ),
        (
            'Статус обработки',
            {
                'fields': ('status',),
            },
        ),
        (
            'Служебная информация',
            {
                'fields': ('created_on',),
            },
        ),
    )
