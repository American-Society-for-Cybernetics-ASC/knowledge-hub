from datetime import datetime

from audit_log.model import AuditPermissionCategory, AuditLog
from auth_module.model import Permissions, PermissionTier
import database
import database.model as model


class AuditLogModule:
    def post_audit(self, category: AuditPermissionCategory, log: str):
        with database.get_session() as session:
            session.add(model.AuditLog(permission_category=category, log=log))
            session.commit()

    def get_audit_logs(
        self,
        categories: list[AuditPermissionCategory],
        before: datetime | None = None,
        after: datetime | None = None,
    ) -> list[AuditLog]:
        with database.get_session() as session:
            query = session.query(model.AuditLog).where(
                model.AuditLog.permission_category.in_(categories)
            )

            if before:
                query = query.where(model.AuditLog.time < before)

            if after:
                query = query.where(model.AuditLog.time > after)

            return [
                AuditLog(category=log.permission_category, log=log.log, time=log.time)
                for log in query
            ]

    @staticmethod
    def all_permitted_audit_categories(
        permissions: Permissions,
    ) -> list[AuditPermissionCategory]:
        return [
            category
            for category in AuditPermissionCategory
            if permissions.includes([category], PermissionTier.manager)
        ]
