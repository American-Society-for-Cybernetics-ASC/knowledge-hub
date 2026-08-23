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
    member_id: int
    status: ApplicationStatus
    submitted_at: datetime | None = None
    content: dict | None = None

class SubmitApplication(BaseModel):
    member_id: int
    content: dict

class ReviseApplication(BaseModel):
    content: dict