from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from cron import cron_module
import database
from settings import SETTINGS


cron_router = APIRouter(prefix="/cron", tags=["cron"])


def cron_guard(request: Request):
    """Check that the caller has authorisation to run cron jobs (Doesn't apply to local deployments)"""
    if SETTINGS.local_deployment:
        return

    if request.headers.get("authorization") != f"Bearer {SETTINGS.cron_secret}":
        raise HTTPException(401, "Unauthorized")


@cron_router.get("/")
def run_cron_jobs(
    _: Annotated[None, Depends(cron_guard)],
):
    with database.with_transaction() as session:
        cron_module.run_cron_jobs(session)
