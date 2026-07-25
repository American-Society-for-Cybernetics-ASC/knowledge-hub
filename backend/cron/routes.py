from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from settings import settings
from .module import CronModule


cron_router = APIRouter()


def cron_guard(request: Request):
    """Check that the caller has authorisation to run cron jobs (Doesn't apply to local deployments)"""
    if settings.local_deployment:
        return

    if request.headers.get("authorization") != f"Bearer {settings.cron_secret}":
        raise HTTPException(401, "Unauthorized")


@cron_router.get("/cron")
def run_cron_jobs(
    module: Annotated[CronModule, Depends(CronModule)],
    _: Annotated[None, Depends(cron_guard)],
):
    module.run_cron_jobs()
