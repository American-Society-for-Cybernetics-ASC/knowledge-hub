from enum import Enum


class MemberStatus(str, Enum):
    CURRENT = "Current"
    EXPIRED = "Expired"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class AuditPermissionCategory(str, Enum):
    mail = "mail"
    payments = "payments"
    auth = "auth"
