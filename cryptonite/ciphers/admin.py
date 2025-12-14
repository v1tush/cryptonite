from django.contrib import admin


from ciphers.models import (
    Cipher,
    CipherComment,
    CipherDayHistory,
    CipherHelp,
    CipherLike,
)


@admin.register(Cipher)
class CipherAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'author',
        'status',
        'difficulty',
        'cipher_type',
        'created_at',
    )
    list_filter = (
        'status',
        'difficulty',
        'cipher_type',
    )
    search_fields = (
        'title',
        'description',
        'author__username',
    )
    ordering = ('-created_at',)


@admin.register(CipherHelp)
class CipherHelpAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cipher',
        'order',
        'created_at',
    )
    list_filter = ('cipher',)
    ordering = ('cipher', 'order')


@admin.register(CipherComment)
class CipherCommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cipher',
        'user',
        'created_at',
    )
    list_filter = ('cipher', 'user')
    search_fields = ('text',)
    ordering = ('-created_at',)


@admin.register(CipherDayHistory)
class CipherDayHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cipher',
        'date',
    )
    list_filter = ('date',)
    ordering = ('-date',)


@admin.register(CipherLike)
class CipherLikeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'cipher',
        'created_at',
    )
    list_filter = ('user', 'cipher')
    ordering = ('-created_at',)
