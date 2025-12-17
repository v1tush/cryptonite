from django.contrib import admin
from django.utils.html import format_html

from qr.models import QR


@admin.register(QR)
class QRAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cipher',
        'qr_preview',
        'created_at',
    )

    readonly_fields = (
        'created_at',
        'qr_preview',
    )

    search_fields = (
        'cipher__title',
    )

    list_select_related = (
        'cipher',
    )

    def qr_preview(self, obj):
        if obj.image and obj.image.storage.exists(obj.image.name):
            return format_html(
                '<img src="{}" style="max-height: 150px;" />',
                obj.image.url,
            )

        return '—'

    qr_preview.short_description = 'QR-код'
