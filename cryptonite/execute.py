from datetime import datetime
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
import scheduler_jobs


def start():
    if any(
        cmd in sys.argv
        for cmd in [
            'createsuperuser',
            'migrate',
            'makemigrations',
            'shell',
            'collectstatic',
        ]
    ):
        return

    scheduler = BackgroundScheduler()
    scheduler.configure(timezone=utc)

    scheduler.add_job(
        scheduler_jobs.setting_daily_cipher,
        'interval',
        seconds=86400,
        next_run_time=datetime.now(utc),
    )
    scheduler.start()
