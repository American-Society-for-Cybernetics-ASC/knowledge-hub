from typing import Annotated

from fastapi import APIRouter, Depends

from mail.module import MailModule
from mail.model import FailedEmail, RedactedEmail


mail_router = APIRouter(prefix="/mail")


@mail_router.get("/failed")
def get_failed_emails(
    module: Annotated[MailModule, Depends(MailModule)],
    # TODO permissions
) -> list[FailedEmail[RedactedEmail]]:
    """Get all failed emails"""
    return list(map(FailedEmail.redact, module.get_failed_emails()))
