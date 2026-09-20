from datetime import datetime

from database.types import PermissionCategory
from utils import BaseModel


class AuditLog(BaseModel):
    category: PermissionCategory
    log: str
    timestamp: datetime
