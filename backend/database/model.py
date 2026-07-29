from sqlalchemy import JSON, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from .base import Base


class Member(Base):
    __tablename__ = "members"

    member_id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False)

    # Add Group table relationsip
    group_id = Column(Integer, ForeignKey("groups.group_id"))
    group = relationship("Group", back_populates="members")
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
    auth_user_id = Column(Integer, ForeignKey("auth_users.user_id"))
    auth_user = relationship("AuthUser", back_populates="members")


class Group(Base):
    __tablename__ = "groups"

    group_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    email = Column(String)

    # relationship to all tables
    members = relationship("Member", back_populates="group")
    memberships = relationship("Membership", back_populates="group")


class Profile(Base):
    __tablename__ = "profiles"

    # Profile is a weak entity
    member_id = Column(Integer, ForeignKey("members.member_id"), primary_key=True)

    tags = Column(JSON)
    content = Column(JSON)

    member = relationship("Member", back_populates="profile")


class Submission(Base):
    __tablename__ = "submissions"

    submission_id = Column(Integer, primary_key=True, index=True)
    provider = Column(String)
    content = Column(JSON)
    tags = Column(JSON)
    status = Column(String)
    title = Column(String)

    # FK to Member table
    member_id = Column(Integer, ForeignKey("members.member_id"))
    member = relationship("Member", back_populates="submissions")

    # FK to Repository table
    repository_id = Column(Integer, ForeignKey("repositories.repository_id"))
    repository = relationship("Repository", back_populates="submissions")


class Repository(Base):
    __tablename__ = "repositories"

    repository_id = Column(Integer, primary_key=True, index=True)
    schema = Column(JSON)

    # Relationships
    submissions = relationship("Submission", back_populates="repository")
    event = relationship("Event", back_populates="repository", uselist=False)


class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    start_time = Column(DateTime)

    # FK and relationship to the Repository table
    repository_id = Column(Integer, ForeignKey("repositories.repository_id"))
    repository = relationship("Repository", back_populates="event")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    status = Column(String)
    kind = Column(String)
    provider = Column(String)

    # Relationship to MemberMatching
    memberships = relationship("Membership", back_populates="payment")


class MemberMatching(Base):
    __tablename__ = "member_matching"

    memMatching_id = Column(Integer, primary_key=True, index=True)

    # Two foreign keys to Member
    active_member_id = Column(Integer, ForeignKey("members.member_id"))
    suggested_member_id = Column(Integer, ForeignKey("members.member_id"))

    # Two relationship  with Member table
    active_member = relationship(
        "Member", foreign_keys=[active_member_id], back_populates="outgoing_matches"
    )

    suggested_member = relationship(
        "Member", foreign_keys=[suggested_member_id], back_populates="incoming_matches"
    )


class Membership(Base):
    __tablename__ = "memberships"

    membership_id = Column(Integer, primary_key=True, index=True)
    start_date = Column(DateTime)
    tier = Column(String)
    status = Column(String)

    # FKs
    member_id = Column(Integer, ForeignKey("members.member_id"))
    group_id = Column(Integer, ForeignKey("groups.group_id"))
    payment_id = Column(Integer, ForeignKey("payments.payment_id"))

    # Relationships
    member = relationship("Member", back_populates="memberships")
    group = relationship("Group", back_populates="memberships")
    payment = relationship("Payment", back_populates="memberships")


class AuthUser(Base):
    __tablename__ = "auth_users"

    user_id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    totp_secret = Column(String)
    totp_enabled = Column(Boolean, default=False)

    failed_attempt = Column(Integer, default=0)
    locked_until = Column(DateTime)

    last_login = Column(DateTime)
    hash_password = Column(String)

    # Relationships
    auth_logs = relationship("AuthLog", back_populates="user")
    members = relationship("Member", back_populates="auth_user")


class AuthLog(Base):
    __tablename__ = "auth_logs"

    auth_log_id = Column(Integer, primary_key=True, index=True)
    log = Column(String)
    time = Column(DateTime)

    # Relationship with AuthUser table
    user_id = Column(Integer, ForeignKey("auth_users.user_id"))
    user = relationship("AuthUser", back_populates="auth_logs")


class Module(Base):
    __tablename__ = "modules"

    module_id = Column(Integer, primary_key=True, index=True)
    config = Column(String)


class CronJobTable(Base):
    __tablename__ = "cron_jobs"

    id = mapped_column(Integer, primary_key=True, index=True)
    enabled = mapped_column(Boolean)
    last_executed = mapped_column(DateTime)
    period = mapped_column(Integer)
    job = mapped_column(JSON)
