from datetime import timezone
from enum import Enum

from sqlalchemy import DateTime, TypeDecorator


class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class PermissionCategory(str, Enum):
    MAIL = "mail"
    PAYMENT = "payment"
    AUTH = "auth"
    MEMBERSHIP = "membership"
    MAILING_LISTS = "mailing_lists"
    NOTIFICATIONS = "notifications"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    REVISION_REQUIRED = "revision_required"

class Currency(str, Enum):
    USD = "usd"
    AUD = "aud"
    NZD = "nzd"
    EUR = "eur"
    GBP = "gbp"
    CAD = "cad"


class ProductType(str, Enum):
    DONATION = "donation"
    CREATE_MEMBERSHIP = "create_membership"
    RENEW_MEMBERSHIP = "renew_membership"


class MailProviderType(str, Enum):
    GMAIL_APP_PASSWORD = "gmail_app_password"


class PaymentProviderType(str, Enum):
    STRIPE = "stripe"
    MOCK = "mock"


class ModuleName(str, Enum):
    NOTIFICATIONS = "notifications"
    MEMBER_MATCHING = "member_matching"
    MEMBERSHIPS = "memberships"


class DuesEmailStep(str, Enum):
    NONE = "none"
    ANNOUNCED = "announced"
    OVERDUE = "overdue"
    OVERDUE_REMINDER = "overdue_reminder"


class CronJobType(str, Enum):
    DUES_REMINDERS = "dues_reminders"


class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not value.tzinfo or value.tzinfo.utcoffset(value) is None:
                raise TypeError("tzinfo is required")
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)
        return value
