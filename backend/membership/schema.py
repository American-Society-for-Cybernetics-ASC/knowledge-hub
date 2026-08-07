from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import Field
from utils import BaseModel

class MembershipStatus(str, Enum):
    CURRENT = "Current"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"
    
class MembershipCreate(BaseModel):
    member_id: int
    tier: str = Field(..., description="Membership tier/plan, e.g. 'Standard', 'Student'")
    group_id: Optional[int] = None  
    
class MembershipRead(BaseModel):
    membership_id: int
    member_id: int
    payment_id: int
    tier: str
    start_date: datetime
    status: MembershipStatus
    
class MembershipActionResult(BaseModel):
    membership: MembershipRead
    message: str
    
class MembershipListParams(BaseModel):
    status: Optional[MembershipStatus] = None
    member_id: Optional[int] = None #Filter to one member's membership
    
class MembershipListResult(BaseModel):
    memberships: list[MembershipRead]
    total: int