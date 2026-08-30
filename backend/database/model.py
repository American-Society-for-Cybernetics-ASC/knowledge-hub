from sqlalchemy import JSON, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base


class Member(Base):
    __tablename__ = "members"

    member_id = mapped_column(Integer, primary_key=True, index=True)
    status = mapped_column(String, nullable=False)

    # Add Group table relationsip
    profile = relationship("Profile", back_populates="member", uselist=False)
    submissions = relationship("Submission", back_populates="member")

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

    memberships = relationship("Membership", back_populates="member")
    auth_user_id = mapped_column(Integer, ForeignKey("auth_users.user_id"))
    auth_user = relationship("AuthUser", back_populates="members")
    mailing_list_memberships = relationship(
        "MailingListMember", back_populates="member"
    )
    applications = relationship("MembershipApplication", back_populates="member")


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
        Integer, ForeignKey("members.member_id"), primary_key=True
    )

    tags = mapped_column(JSON)
    content = mapped_column(JSON)

    member = relationship("Member", back_populates="profile")


class Submission(Base):
    __tablename__ = "submissions"

    submission_id = mapped_column(Integer, primary_key=True, index=True)
    provider = mapped_column(String)
    content = mapped_column(JSON)
    tags = mapped_column(JSON)
    status = mapped_column(String, nullable=False)
    title = mapped_column(String, nullable=False)

    # FK to Member table
    member_id = mapped_column(Integer, ForeignKey("members.member_id"))
    member = relationship("Member", back_populates="submissions")

    # FK to Repository table
    repository_id = mapped_column(Integer, ForeignKey("repositories.repository_id"))
    repository = relationship("Repository", back_populates="submissions")


class Repository(Base):
    __tablename__ = "repositories"

    repository_id = mapped_column(Integer, primary_key=True, index=True)
    schema = mapped_column(JSON)

    # Relationships
    submissions = relationship("Submission", back_populates="repository")
    event = relationship("Event", back_populates="repository", uselist=False)


class Event(Base):
    __tablename__ = "events"

    event_id = mapped_column(Integer, primary_key=True, index=True)
    title = mapped_column(String, nullable=False)
    content = mapped_column(String)
    start_time = mapped_column(DateTime)

    # FK and relationship to the Repository table
    repository_id = Column(Integer, ForeignKey("repositories.repository_id"))
    repository = relationship("Repository", back_populates="event")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = mapped_column(Integer, primary_key=True, index=True)
    date = mapped_column(DateTime, nullable=False)
    status = mapped_column(String, nullable=False)
    kind = mapped_column(String, nullable=False)
    transaction = mapped_column(JSON, nullable=False)


class MemberMatching(Base):
    __tablename__ = "member_matching"

    memMatching_id = mapped_column(Integer, primary_key=True, index=True)

    # Two foreign keys to Member
    active_member_id = mapped_column(Integer, ForeignKey("members.member_id"))
    suggested_member_id = mapped_column(Integer, ForeignKey("members.member_id"))

    # Two relationship  with Member table
    active_member = relationship(
        "Member", foreign_keys=[active_member_id], back_populates="outgoing_matches"
    )

    suggested_member = relationship(
        "Member", foreign_keys=[suggested_member_id], back_populates="incoming_matches"
    )


class Membership(Base):
    __tablename__ = "memberships"

    membership_id = mapped_column(Integer, primary_key=True, index=True)
    start_date = mapped_column(DateTime, nullable=False)
    membership_expires = mapped_column(DateTime, nullable=False)
    tier = mapped_column(String, nullable=False)
    status = mapped_column(String, nullable=False)

    # FKs
    member_id = mapped_column(Integer, ForeignKey("members.member_id"))

    # Relationships
    member = relationship("Member", back_populates="memberships")


class AuthUser(Base):
    __tablename__ = "auth_users"

    user_id = mapped_column(Integer, primary_key=True, index=True)

    name = mapped_column(String)
    email = mapped_column(String, unique=True, index=True, nullable=False)
    permissions = mapped_column(JSON)

    created_at = mapped_column(DateTime)
    updated_at = mapped_column(DateTime)

    totp_secret = mapped_column(String)
    totp_enabled = mapped_column(Boolean, default=False, nullable=False)

    failed_attempt = mapped_column(Integer, default=0)
    locked_until = mapped_column(DateTime)
    admin_locked = mapped_column(Boolean, default=False)

    last_login = mapped_column(DateTime)
    hash_password = mapped_column(String)

    # Relationships
    auth_logs = relationship("AuthLog", back_populates="user")
    members = relationship("Member", back_populates="auth_user")


class AuthLog(Base):
    __tablename__ = "auth_logs"

    auth_log_id = mapped_column(Integer, primary_key=True, index=True)
    log = mapped_column(String, nullable=False)
    time = mapped_column(DateTime)

    # Relationship with AuthUser table
    user_id = mapped_column(Integer, ForeignKey("auth_users.user_id"))
    user = relationship("AuthUser", back_populates="auth_logs")


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
    member_id = mapped_column(Integer, ForeignKey("members.member_id"), nullable=True)

    # relationships
    mailing_list = relationship("MailingList", back_populates="members")
    member = relationship("Member", back_populates="mailing_list_memberships")


class CronJobTable(Base):
    __tablename__ = "cron_jobs"

    id = mapped_column(Integer, primary_key=True, index=True)
    enabled = mapped_column(Boolean)
    last_executed = mapped_column(DateTime)
    period = mapped_column(Integer)
    job = mapped_column(JSON)


class FailedEmailTable(Base):
    __tablename__ = "failed_emails"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    last_sent = mapped_column(DateTime, server_default=func.now())
    retries = mapped_column(Integer, default=0)
    email = mapped_column(JSON)
    error = mapped_column(String, nullable=True)


class MembershipApplication(Base):
    __tablename__ = "membership_applications"

    application_id = mapped_column(Integer, primary_key=True, index=True)
    status = mapped_column(
        String, nullable=False
    )  # pending, approved, denied, revision_requested
    submitted_at = mapped_column(DateTime)
    content = mapped_column(JSON)  # the application form's fields

    member_id = mapped_column(Integer, ForeignKey("members.member_id"))
    member = relationship("Member", back_populates="applications")


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("auth_users.user_id"))
    subject = mapped_column(String, nullable=False)
    message = mapped_column(String, nullable=False)
    read = mapped_column(Boolean, default="False")
    created_at = mapped_column(DateTime, server_default=func.now())

    # Relationship
    user = relationship("AuthUser")
