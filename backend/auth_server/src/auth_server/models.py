from enum import Enum
from datetime import datetime
from uuid import UUID

class RegistrationRequest:
    """
    Represents the data sent by the frontend
    when a user registers a new account.
    """
    email: str
    password: str
    display_name: str


class LoginRequest:
    """
    Represents the data sent by the frontend
    when a user attempts to login.
    """
    email: str
    password: str
    

class Role(Enum):
    GUEST = "guest"
    MEMBER = "member"
    MODERATOR = "moderator"
    MANAGER = "manager"
    ADMIN = "admin"


class MemberStatus(Enum):
    NEW = "new"
    ACTIVE = "active"
    DORMANT = "dormant"
    ARCHIVED = "archived"
    DECEASED = "deceased"
    RESIGNED = "resigned"
    

class UserAccount:
    """
    Represents a user account stored in the database.
    Contains credentials, role, and account status.
    """

    id: UUID
    email: str
    hashed_password: str
    totp_secret: str
    totp_enabled: bool
    role: dict
    status: MemberStatus
    failed_attempts: int
    locked_until: datetime
    admin_locked: bool
    created_at: datetime
    last_login: datetime