from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management.base import BaseCommand
from django.utils import timezone

from scheduler_jobs import select_daily_cipher


class Command(BaseCommand):
    help = (
        'Select the daily cipher at midnight, with retries every 15 minutes.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--once', action='store_true')

    def handle(self, *args, **options):
        select_daily_cipher()
        if options['once']:
            return

        scheduler = BlockingScheduler(timezone=timezone.get_default_timezone())
        scheduler.add_job(
            select_daily_cipher,
            trigger='cron',
            minute='*/15',
            id='daily_cipher',
            coalesce=True,
            max_instances=1,
            misfire_grace_time=3600,
        )
        self.stdout.write('Starting APScheduler...')
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            if scheduler.running:
                scheduler.shutdown()
