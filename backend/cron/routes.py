from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from auth_module import PermissionTier, authorized
from settings import SETTINGS
from .module import CronModule, CronJob


cron_router = APIRouter(prefix="/cron", tags=["cron"])


def cron_guard(request: Request):
    """Check that the caller has authorisation to run cron jobs (Doesn't apply to local deployments)"""
    if SETTINGS.local_deployment:
        return

    if request.headers.get("authorization") != f"Bearer {SETTINGS.cron_secret}":
        raise HTTPException(401, "Unauthorized")


@cron_router.get("/")
def run_cron_jobs(
    module: Annotated[CronModule, Depends(CronModule)],
    _: Annotated[None, Depends(cron_guard)],
):
    now = datetime.now(timezone.utc)
    for queued_job in module.get_queued_cron_jobs():
        queued_job.job.execute()
        queued_job.last_executed = now
        module.patch_cron_job(queued_job)


@cron_router.get("/queued_jobs")
def get_queued_jobs(
    module: Annotated[CronModule, Depends(CronModule)],
    _=Depends(authorized([], PermissionTier.adminstrator)),
) -> list[CronJob]:
    return module.get_queued_cron_jobs()


@cron_router.get("/jobs")
def get_all_jobs(
    module: Annotated[CronModule, Depends(CronModule)],
    _=Depends(authorized([], PermissionTier.adminstrator)),
) -> list[CronJob]:
    return module.get_all_cron_jobs()
