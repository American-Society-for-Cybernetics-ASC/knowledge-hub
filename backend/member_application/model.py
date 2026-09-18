from enum import Enum
from uuid import UUID
from utils import BaseModel
from datetime import datetime


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    REVISION_REQUIRED = "revision_required"


class MemberApplication(BaseModel):
    application_id: int
    auth_user_id: int
    member_type_id: UUID | None
    status: ApplicationStatus
    submitted_at: datetime | None = None
    content: str | None = None


class SubmitApplication(BaseModel):
    content: str


class ReviseApplication(BaseModel):
    content: str
