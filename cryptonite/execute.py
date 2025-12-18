from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import utc
import scheduler_jobs


def start_scheduler():
    scheduler = BlockingScheduler(timezone=utc)

    scheduler.add_job(
        scheduler_jobs.setting_daily_cipher,
        trigger='interval',
        seconds=86400,
        next_run_time=datetime.now(utc),
        id='daily_cipher',
        replace_existing=True,
    )

    scheduler.start()
