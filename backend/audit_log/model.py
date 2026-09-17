from datetime import datetime

from database.types import AuditPermissionCategory
from utils import BaseModel


class AuditLog(BaseModel):
    category: AuditPermissionCategory
    log: str
    time: datetime
