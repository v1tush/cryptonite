from django.core.exceptions import ImproperlyConfigured
from django.http.request import split_domain_port


def validate_production_settings(secret_key, allowed_hosts):
    if (
        len(secret_key) < 50
        or len(set(secret_key)) < 5
        or secret_key != secret_key.strip()
        or secret_key.lower().startswith(
            ('django-insecure-', 'fake', 'change-me', 'replace-me', 'example'),
        )
    ):
        raise ImproperlyConfigured(
            'DJANGO_SECRET_KEY must be a unique random key of at least 50 '
            'characters when DJANGO_DEBUG=False.',
        )

    if not allowed_hosts or any(
        not split_domain_port(host)[0]
        or split_domain_port(host)[1]
        or host.startswith(('.', '-'))
        for host in allowed_hosts
    ):
        raise ImproperlyConfigured(
            'DJANGO_ALLOWED_HOSTS must list explicit hosts without '
            'wildcards, schemes or ports when DJANGO_DEBUG=False.',
        )
