from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ciphers.constants import HINT_PRICE
from ciphers.models import Cipher, CipherHelp

DEMO_PASSWORD = 'Cryptonite-demo-only!42'


class Command(BaseCommand):
    help = (
        'Load a repeatable local demo without changing existing gameplay data.'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                'Demo accounts are available only with DJANGO_DEBUG=True.'
            )

        author = self.get_demo_user('demo_author')
        self.get_demo_user('demo_player', money=HINT_PRICE)
        cipher, created = Cipher.objects.get_or_create(
            author=author,
            title='Демо: шифр Цезаря',
            defaults={
                'encrypted_phrase': 'KHOOR ZRUOG',
                'answer_phrase': 'HELLO WORLD',
                'description': (
                    'Каждая буква английского алфавита была сдвинута на '
                    'одинаковое количество позиций вперёд. Пробел между '
                    'словами оставлен без изменений.'
                ),
                'difficulty': 1,
                'status': 'approved',
                'attempt_limit': 2,
            },
        )
        if created:
            CipherHelp.objects.create(
                cipher=cipher,
                text='Сдвиньте каждую букву на три позиции назад.',
                order=1,
            )
        self.stdout.write(
            self.style.SUCCESS(f'Demo cipher: {cipher.get_absolute_url()}')
        )

    def get_demo_user(self, username, **defaults):
        email = f'{username}@example.invalid'
        user, created = get_user_model().objects.get_or_create(
            username=username,
            defaults={'email': email, **defaults},
        )
        if not created and user.email != email:
            raise CommandError(f'The username {username} is already in use.')
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=['password'])
        return user
