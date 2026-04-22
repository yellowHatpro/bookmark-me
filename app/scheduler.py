import logging
import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from app.config import get_settings
from app.db import SessionLocal
from app.models import Account
from app.sync_service import run_sync

log = logging.getLogger(__name__)

_JOB_PREFIX = "sync-account-"


class SyncScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def schedule_account(self, account_id: int) -> None:
        settings = get_settings()
        job_id = f"{_JOB_PREFIX}{account_id}"
        self.scheduler.add_job(
            run_sync,
            IntervalTrigger(
                minutes=settings.sync_interval_min,
                jitter=60,
            ),
            args=[account_id],
            id=job_id,
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
            next_run_time=_jittered_first_run(),
        )
        log.info("Scheduled sync for account %s every %s min", account_id, settings.sync_interval_min)

    def unschedule_account(self, account_id: int) -> None:
        job_id = f"{_JOB_PREFIX}{account_id}"
        try:
            self.scheduler.remove_job(job_id)
        except Exception:
            pass

    async def reload_from_db(self) -> None:
        async with SessionLocal() as session:
            result = await session.execute(select(Account.id))
            for (account_id,) in result.all():
                self.schedule_account(account_id)


def _jittered_first_run():
    from datetime import datetime, timedelta, timezone

    return datetime.now(timezone.utc) + timedelta(seconds=random.randint(15, 60))


scheduler = SyncScheduler()
