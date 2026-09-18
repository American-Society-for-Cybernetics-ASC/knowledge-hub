from datetime import datetime
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
    AuditPermissionCategory,
    PaymentStatus,
    TransactionStatus,
    TZDateTime,
)

from .base import Base


class Member(Base):
    __tablename__ = "members"

    auth_user_id = mapped_column(
        Integer, ForeignKey("auth_users.user_id"), primary_key=True
    )
    membership_expires: Mapped[datetime] = mapped_column(TZDateTime, nullable=False)
    member_type_id = mapped_column(UUID, ForeignKey("member_types.id"), nullable=True)
    cancelled = mapped_column(Boolean, nullable=False, default=False)

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
    member_id = mapped_column(
        Integer, ForeignKey("members.auth_user_id"), primary_key=True
    )

    tags = mapped_column(JSON)
    content = mapped_column(JSON)

    # Members can opt out of matching
    matching_opt_out = mapped_column(Boolean, nullable=False, default=False)

    member = relationship("Member", back_populates="profile")


class Payment(Base):
    __tablename__ = "payments"

    id = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    user_id = mapped_column(Integer, ForeignKey(Member.auth_user_id), nullable=False)
    time = mapped_column(TZDateTime, nullable=False, server_default=func.now())
    amount = mapped_column(Integer, nullable=False)
    currency = mapped_column(String, nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(String, nullable=False)
    product = mapped_column(JSON, nullable=False)

    transactions = relationship("Transaction", back_populates="payment")


class Transaction(Base):
    __tablename__ = "transactions"

    id = mapped_column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    payment_id = mapped_column(UUID, ForeignKey(Payment.id), nullable=False)
    data = mapped_column(JSON, nullable=False)
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
        ForeignKey(Member.auth_user_id),
        nullable=False,
    )
    suggested_member_id = mapped_column(
        Integer,
        ForeignKey(Member.auth_user_id),
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

    name = mapped_column(String)
    email = mapped_column(String, unique=True, index=True, nullable=False)
    permissions = mapped_column(JSON)

    created_at = mapped_column(TZDateTime)
    updated_at = mapped_column(TZDateTime)

    totp_secret = mapped_column(String)
    totp_enabled = mapped_column(Boolean, default=False, nullable=False)

    failed_attempt = mapped_column(Integer, default=0)
    locked_until = mapped_column(TZDateTime)
    admin_locked = mapped_column(Boolean, default=False)

    last_login = mapped_column(TZDateTime)
    hash_password = mapped_column(String)


class AuditLog(Base):
    __tablename__ = "auth_logs"

    auth_log_id = mapped_column(Integer, primary_key=True, index=True)
    permission_category: Mapped[AuditPermissionCategory] = mapped_column(
        String, nullable=False
    )
    log = mapped_column(String, nullable=False)
    time = mapped_column(TZDateTime, server_default=func.now(), nullable=False)


class Module(Base):
    __tablename__ = "modules"

    module_name = mapped_column(String, primary_key=True, index=True)
    config = mapped_column(JSON)


class MailingListMember(Base):
    __tablename__ = "mailing_list_members"

    mailing_list_member_id = mapped_column(Integer, primary_key=True, index=True)

    mailing_list_id = mapped_column(
        Integer, ForeignKey("mailing_lists.mailing_list_id"), nullable=False
    )

    email = mapped_column(String, nullable=False)
    # nullable for external emails
    member_id = mapped_column(
        Integer, ForeignKey("members.auth_user_id"), nullable=True
    )

    # relationships
    mailing_list = relationship("MailingList", back_populates="members")
    member = relationship("Member", back_populates="mailing_list_memberships")


class CronJobTable(Base):
    __tablename__ = "cron_jobs"

    id = mapped_column(Integer, primary_key=True, index=True)
    enabled = mapped_column(Boolean, nullable=False)
    last_executed = mapped_column(TZDateTime, nullable=False)
    period = mapped_column(Integer, nullable=False)
    job = mapped_column(JSON, nullable=False)


class FailedEmailTable(Base):
    __tablename__ = "failed_emails"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    last_sent = mapped_column(TZDateTime, server_default=func.now())
    retries = mapped_column(Integer, default=0)
    email = mapped_column(JSON)
    error = mapped_column(String, nullable=True)


class MembershipApplication(Base):
    __tablename__ = "membership_applications"

    application_id = mapped_column(Integer, primary_key=True, index=True)
    auth_user_id = mapped_column(Integer, ForeignKey(AuthUser.user_id), nullable=False)
    member_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID, ForeignKey("member_types.id"), nullable=True
    )
    """None for out-of-date membership types"""
    status = mapped_column(
        String, nullable=False
    )  # pending, approved, denied, revision_requested
    submitted_at = mapped_column(TZDateTime, server_default=func.now(), nullable=False)
    content = mapped_column(String, nullable=False)  # the application form's fields

    member_type: Mapped[MemberType | None] = relationship(
        "MemberType", foreign_keys=[member_type_id]
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
