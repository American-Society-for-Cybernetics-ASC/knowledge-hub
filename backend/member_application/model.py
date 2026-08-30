from enum import Enum
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
    status: ApplicationStatus
    submitted_at: datetime | None = None
    content: str | None = None

class SubmitApplication(BaseModel):
    content: str

class ReviseApplication(BaseModel):
    content: str