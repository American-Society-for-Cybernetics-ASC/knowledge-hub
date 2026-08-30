from datetime import datetime

from .enums import AuditPermissionCategory
from utils import BaseModel


class AuditLog(BaseModel):
    category: AuditPermissionCategory
    log: str
    time: datetime
