from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from audit_log.module import AuditLogModule
from audit_log.model import AuditLog, AuditPermissionCategory
from auth_module import PermissionTier, Permissions, permissions


audit_router = APIRouter(prefix="/audit_log", tags=["auditlog"])


@audit_router.get("")
def get_logs(
    module: Annotated[AuditLogModule, Depends(AuditLogModule)],
    permissions: Annotated[Permissions, Depends(permissions)],
    after: datetime | None = None,
    before: datetime | None = None,
    categories: list[AuditPermissionCategory] | None = Query(None, alias="category"),
) -> list[AuditLog]:
    """
    Get all logs, filtered by
    """
    # Verify permissions
    if categories is not None:
        for category in categories:
            if not permissions.includes([category], PermissionTier.manager):
                raise HTTPException(401, "Unauthorized")
    else:
        categories = module.all_permitted_audit_categories(permissions)

    return module.get_audit_logs(categories=categories, before=before, after=after)
