from fastapi import APIRouter, Depends

from auth_module import authorized
from auth_module.model import PermissionTier
import database
from database.types import PermissionCategory
from .model import FailedEmail, RedactedEmail
from . import mail_module


mail_router = APIRouter(prefix="/mail", tags=["mail"])


@mail_router.get("/failed")
def get_failed_emails(
    _=Depends(authorized([PermissionCategory.MAIL], PermissionTier.manager)),
) -> list[FailedEmail[RedactedEmail]]:
    """Get all failed emails"""
    with database.with_transaction() as session:
        return list(map(FailedEmail.redact, mail_module.get_failed_emails(session)))
