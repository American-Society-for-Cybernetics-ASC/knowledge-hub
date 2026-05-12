from enum import Enum
from datetime import datetime
from uuid import UUID


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
    role: Role
    status: MemberStatus
    failed_attempts: int
    locked_until: datetime
    admin_locked: bool
    created_at: datetime
    last_login: datetime