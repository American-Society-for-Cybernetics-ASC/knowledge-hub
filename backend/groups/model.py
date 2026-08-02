from typing import Optional
from pydantic import BaseModel

class Group(BaseModel):
    model_config = {"from_attributes": True}

    group_id: int
    name: str
    description: Optional[str] = None
    email: Optional[str] = None

class GroupMember(BaseModel):
    """represents a member of a group"""
    model_config = {"from_attributes": True}

    member_id: int
    status: str
    group_id: Optional[int] = None

class MailingListMember(BaseModel):
    """represents any email address on a mailing list including non-members emails"""
    model_config = {"from_attributes": True}
    
    email: str
    is_member: bool
    member_id: Optional[int] = None