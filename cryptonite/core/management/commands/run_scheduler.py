from django.core.management.base import BaseCommand
from execute import start_scheduler


class Command(BaseCommand):
    help = 'Run APScheduler'

    def handle(self, *args, **options):
        self.stdout.write('Starting APScheduler...')
        start_scheduler()
