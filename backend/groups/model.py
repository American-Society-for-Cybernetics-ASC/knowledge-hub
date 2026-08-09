from typing import Optional
from utils import BaseModel

class Group(BaseModel):
    group_id: int
    name: str
    description: Optional[str] = None
    email: Optional[str] = None

class GroupMember(BaseModel):
    """represents a member of a group"""
    member_id: int
    status: str
    group_id: Optional[int] = None

class MailingListMember(BaseModel):
    """represents any email address on a mailing list including non-members emails"""
    email: str
    member_id: Optional[int] = None