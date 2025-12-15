from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
import django.urls

urlpatterns = [
    django.urls.path('i18n/', django.urls.include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    django.urls.path('admin/', admin.site.urls),
    django.urls.path('users/', django.urls.include('users.urls')),
    django.urls.path('about/', django.urls.include('about.urls')),
    django.urls.path('core/', django.urls.include('core.urls')),
    django.urls.path('ciphers/', django.urls.include('ciphers.urls')),
    django.urls.path('feedback/', django.urls.include('feedback.urls')),
    django.urls.path('courses/', django.urls.include('courses.urls')),
    django.urls.path(
        'notifications/',
        django.urls.include('notifications.urls'),
    ),
    django.urls.path('', django.urls.include('main.urls')),
    prefix_default_language=False,
)

if django.conf.settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
