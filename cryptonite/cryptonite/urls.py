from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
import django.urls

urlpatterns = [
    django.urls.path('i18n/', django.urls.include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    django.urls.path('admin/', admin.site.urls),
    django.urls.path('users/', django.urls.include('users.urls')),
    django.urls.path('about/', django.urls.include('about.urls')),
    django.urls.path('', django.urls.include('main.urls')),
    prefix_default_language=False,
)
