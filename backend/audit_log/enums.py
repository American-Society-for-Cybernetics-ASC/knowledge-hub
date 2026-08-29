from enum import Enum


class AuditPermissionCategory(str, Enum):
    mail = "mail"
    payments = "payments"
    auth = "auth"
