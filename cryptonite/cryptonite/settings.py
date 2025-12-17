from pathlib import Path

from django.utils.translation import gettext_lazy as _
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

env.read_env(BASE_DIR.parent / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY', default='fake-key')

DEBUG = env.bool('DJANGO_DEBUG', default='False')

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['*'])

SITE_URL = '127.0.0.1:8000'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'about.apps.AboutConfig',
    'achievements.apps.AchievementsConfig',
    'core.apps.CoreConfig',
    'courses.apps.CoursesConfig',
    'ciphers.apps.CiphersConfig',
    'feedback.apps.FeedbackConfig',
    'logs.apps.LogsConfig',
    'main.apps.MainConfig',
    'notifications.apps.NotificationsConfig',
    'qr.apps.QrConfig',
    'users.apps.UsersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cryptonite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'core.context_processors.count_pending_ciphers',
            ],
        },
    },
]

WSGI_APPLICATION = 'cryptonite.wsgi.application'

AUTH_USER_MODEL = 'users.CustomUser'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DJANGO_DB_NAME', default='cryptonite_db'),
        'USER': env('DJANGO_DB_USER', default='cryptonite_user'),
        'PASSWORD': env('DJANGO_DB_PASSWORD', default='password'),
        'HOST': env('DJANGO_DB_HOST', default='db'),
        'PORT': env('DJANGO_DB_PORT', default='5432'),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.NumericPasswordValidator',
    },
]

LOCALE_PATHS = [BASE_DIR / 'locale']

LANGUAGES = [
    ('ru', _('Русский')),
    ('en', _('English')),
]

LANGUAGE_CODE = env('DJANGO_LANGUAGE_CODE', default='ru')

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR / 'static_dev']

STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_URL = 'users:login'

LOGIN_REDIRECT_URL = 'main:main'

LOGOUT_REDIRECT_URL = 'users:login'
