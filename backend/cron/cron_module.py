import datetime
from typing import Iterable

from membership import membership_module
from database.types import CronJobType
from database.model import CronJob

from sqlalchemy.orm import Session


def _job_list() -> Iterable[CronJobType]:
    """Indirection for use in mocking"""
    return CronJobType


def _now() -> datetime.datetime:
    """Indirection for use in mocking"""
    return datetime.datetime.now(datetime.timezone.utc)


def get_job(session: Session, job_type: CronJobType) -> CronJob:
    job = session.get(CronJob, job_type)
    if job is None:
        with session.begin_nested():
            job = CronJob(job_type=job_type)
            session.add(job)
    return job


def run_cron_jobs(session: Session):
    now = _now()

    for job_type in _job_list():
        job = get_job(session, job_type)
        enabled = handle_get_cron_job_period(job_type)
        if not enabled:
            continue

        # Vercel only promises +-1 hour precision at the hobby tier.
        # So we include a 2 hour slack time
        period = handle_get_cron_job_period(job_type) - datetime.timedelta(hours=2)
        if (now - job.last_executed) < period:
            return
        handle_run_cron_job(session, job_type)
        job.last_executed = now


def handle_get_cron_job_period(job: CronJobType) -> datetime.timedelta:
    """Usually this is stored in a particular module's config"""
    match job:
        case CronJobType.DUES_REMINDERS:
            return datetime.timedelta(days=1)


def handle_get_cron_job_enabled(job: CronJobType) -> bool:
    """Usually this is stored in a particular module's config"""
    match job:
        case CronJobType.DUES_REMINDERS:
            return True


def handle_run_cron_job(session: Session, job: CronJobType):
    """Forward to the appropriate handler"""
    match job:
        case CronJobType.DUES_REMINDERS:
            membership_module.send_membership_dues_reminders(session)
