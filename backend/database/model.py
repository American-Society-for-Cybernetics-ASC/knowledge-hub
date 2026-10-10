from abc import abstractmethod
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import (
    JSON,
    UUID,
    Integer,
    String,
    Boolean,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .types import (
    ApplicationStatus,
    MailProviderType,
    ModuleName,
    PaymentProviderType,
    PermissionCategory,
    PaymentStatus,
    ProductType,
    TransactionStatus,
    TZDateTime,
)

from .base import Base


class Member(Base):
    __tablename__ = "members"

    user_id = mapped_column(Integer, ForeignKey("auth_users.user_id"), primary_key=True)
    due_date: Mapped[datetime] = mapped_column(TZDateTime, nullable=False)
    member_type_id = mapped_column(UUID, ForeignKey("member_types.id"), nullable=True)
    cancelling = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    profile = relationship("Profile", back_populates="member", uselist=False)
    member_type: Mapped[MemberType | None] = relationship(
        "MemberType", uselist=False, lazy="joined"
    )
    mailing_list_memberships = relationship(
        "MailingListMember", back_populates="member"
    )
    outgoing_matches = relationship(
        "MemberMatching",
        foreign_keys="MemberMatching.active_member_id",
        back_populates="active_member",
    )
    incoming_matches = relationship(
        "MemberMatching",
        foreign_keys="MemberMatching.suggested_member_id",
        back_populates="suggested_member",
    )

    auth_user: Mapped[AuthUser] = relationship("AuthUser")


class MailingList(Base):
    __tablename__ = "mailing_lists"

    mailing_list_id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, nullable=False)
    description = mapped_column(String)
    email = mapped_column(String)

    members = relationship("MailingListMember", back_populates="mailing_list")


class Profile(Base):
    __tablename__ = "profiles"

    # Profile is a weak entity
    member_id = mapped_column(Integer, ForeignKey("members.user_id"), primary_key=True)

    tags: Mapped[list | None] = mapped_column(JSON)
    content: Mapped[dict | None] = mapped_column(JSON)

    # Members can opt out of matching
    matching_opt_out = mapped_column(Boolean, nullable=False, default=False)

    member = relationship("Member", back_populates="profile")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True, default=uuid.uuid4
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("auth_users.user_id"))
    timestamp: Mapped[datetime] = mapped_column(TZDateTime, server_default=func.now())
    amount: Mapped[int]
    currency: Mapped[str]
    status: Mapped[PaymentStatus] = mapped_column(default=PaymentStatus.PENDING)
    product: Mapped[ProductType]

    @abstractmethod
    def product_description(self) -> str: ...

    __mapper_args__ = {
        "polymorphic_abstract": True,
        "polymorphic_on": "product",
    }

    transactions = relationship("Transaction", back_populates="payment")


class Transaction(Base):
    __tablename__ = "transactions"

    id = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    payment_id = mapped_column(UUID, ForeignKey(Payment.id), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    last_known_status: Mapped[TransactionStatus] = mapped_column(
        String, nullable=False, default=TransactionStatus.PENDING
    )

    payment = relationship("Payment", back_populates="transactions")


class MemberMatching(Base):
    __tablename__ = "member_matching"
    __table_args__ = (
        UniqueConstraint(
            "active_member_id",
            "suggested_member_id",
            name="uq_member_matching_directed_pair",
        ),
        CheckConstraint(
            "active_member_id != suggested_member_id",
            name="ck_member_matching_no_self_match",
        ),
    )

    memMatching_id = mapped_column(Integer, primary_key=True, index=True)

    # Two foreign keys to Member
    active_member_id = mapped_column(
        Integer,
        ForeignKey(Member.user_id),
        nullable=False,
    )
    suggested_member_id = mapped_column(
        Integer,
        ForeignKey(Member.user_id),
        nullable=False,
    )

    # Used later to calc the dismissal period
    dismissed_at = mapped_column(TZDateTime, nullable=False)

    # Two relationships with Member table
    active_member = relationship(
        "Member",
        foreign_keys=[active_member_id],
        back_populates="outgoing_matches",
    )
    suggested_member = relationship(
        "Member",
        foreign_keys=[suggested_member_id],
        back_populates="incoming_matches",
    )


class AuthUser(Base):
    __tablename__ = "auth_users"

    user_id = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[Optional[str]] = mapped_column(String)
    email = mapped_column(String, unique=True, index=True, nullable=False)
    permissions: Mapped[dict | None] = mapped_column(JSON)

    created_at = mapped_column(TZDateTime)
    updated_at = mapped_column(TZDateTime)

    totp_secret = mapped_column(String)
    totp_enabled = mapped_column(Boolean, default=False, nullable=False)

    failed_attempt = mapped_column(Integer, default=0)
    locked_until = mapped_column(TZDateTime)
    admin_locked = mapped_column(Boolean, default=False)

    last_login = mapped_column(TZDateTime)
    hash_password = mapped_column(String)

    applications: Mapped[list[MembershipApplication]] = relationship()


class AuditLog(Base):
    __tablename__ = "auth_logs"

    auth_log_id = mapped_column(Integer, primary_key=True, index=True)
    permission_category: Mapped[PermissionCategory] = mapped_column(
        String, nullable=False
    )
    log = mapped_column(String, nullable=False)
    timestamp = mapped_column(TZDateTime, server_default=func.now(), nullable=False)


class ModuleConfig(Base):
    """Polymorphic: see module_configs.py for subclasses"""

    __tablename__ = "module_configs"

    # This is a primary key: i.e. there is precisely one config for each module.
    module_name: Mapped[ModuleName] = mapped_column(primary_key=True, index=True)

    __mapper_args__ = {
        "polymorphic_abstract": True,
        "polymorphic_on": "module_name",
    }


class MailingListMember(Base):
    __tablename__ = "mailing_list_members"

    mailing_list_member_id = mapped_column(Integer, primary_key=True, index=True)

    mailing_list_id = mapped_column(
        Integer, ForeignKey("mailing_lists.mailing_list_id"), nullable=False
    )

    email = mapped_column(String, nullable=False)
    # nullable for external emails
    member_id = mapped_column(Integer, ForeignKey("members.user_id"), nullable=True)

    # relationships
    mailing_list = relationship("MailingList", back_populates="members")
    member = relationship("Member", back_populates="mailing_list_memberships")


class CronJobTable(Base):
    __tablename__ = "cron_jobs"

    id = mapped_column(Integer, primary_key=True, index=True)
    enabled = mapped_column(Boolean, nullable=False)
    last_executed = mapped_column(TZDateTime, nullable=False)
    period = mapped_column(Integer, nullable=False)
    job: Mapped[dict] = mapped_column(JSON, nullable=False)


class MailSender(Base):
    """A sender that a mail manager has configured. Polymorphic: see mail_providers.py for subclasses"""

    __tablename__ = "mail_senders"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True, default=uuid.uuid7
    )
    name: Mapped[str]
    description: Mapped[str]
    provider: Mapped[MailProviderType]

    __mapper_args__ = {
        "polymorphic_abstract": True,
        "polymorphic_on": "provider",
    }


class PaymentOption(Base):
    """An option a manager has configured for users to use to pay. Polymorphic: see payment_providers.py for subclasses"""

    __tablename__ = "payment_options"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True, default=uuid.uuid7
    )
    name: Mapped[str]
    description: Mapped[str]
    provider: Mapped[PaymentProviderType]

    __mapper_args__ = {
        "polymorphic_abstract": True,
        "polymorphic_on": "provider",
    }


class FailedEmailTable(Base):
    __tablename__ = "failed_emails"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    last_sent = mapped_column(TZDateTime, server_default=func.now())
    retries = mapped_column(Integer, default=0)
    email: Mapped[dict | None] = mapped_column(JSON)
    error = mapped_column(String, nullable=True)


class MembershipApplication(Base):
    __tablename__ = "membership_applications"

    application_id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey(AuthUser.user_id), nullable=False)
    member_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID, ForeignKey("member_types.id"), nullable=True
    )
    """None for out-of-date membership types"""
    status: Mapped[ApplicationStatus] = mapped_column(
        String, nullable=False
    )  # pending, approved, denied, revision_requested
    submitted_at = mapped_column(TZDateTime, server_default=func.now(), nullable=False)
    last_edited: Mapped[datetime] = mapped_column(
        TZDateTime, server_default=func.now(), nullable=False
    )
    content = mapped_column(String, nullable=False)  # the application form's fields

    member_type: Mapped[MemberType | None] = relationship(
        "MemberType", foreign_keys=[member_type_id], lazy="joined"
    )
    user: Mapped[AuthUser] = relationship(
        AuthUser, foreign_keys=[user_id], back_populates="applications"
    )


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("auth_users.user_id"))
    subject = mapped_column(String, nullable=False)
    message = mapped_column(String, nullable=False)
    read = mapped_column(Boolean, default="False")
    created_at = mapped_column(TZDateTime, server_default=func.now())

    # Relationship
    user = relationship("AuthUser")


class MemberType(Base):
    __tablename__ = "member_types"

    id = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    name = mapped_column(String, nullable=False)
    price = mapped_column(Integer, nullable=False)


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    name = mapped_column(String, primary_key=True, index=True)
    subject = mapped_column(String, nullable=False)
    body = mapped_column(String, nullable=False)
    variables: Mapped[list[str]] = mapped_column(JSON, nullable=False)
