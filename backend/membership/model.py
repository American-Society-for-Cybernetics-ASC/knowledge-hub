from datetime import datetime, timezone
from enum import Enum
from uuid import UUID

from utils import BaseModel
from database import model as dbmodel


class MemberStatus(str, Enum):
    PENDING = "Pending"
    CURRENT = "Current"
    OVERDUE = "Overdue"
    EXPIRED = "Expired"

    @staticmethod
    def calc_expiry(expiry_date: datetime) -> MemberStatus:
        return (
            MemberStatus.CURRENT
            if expiry_date > datetime.now(timezone.utc)
            else MemberStatus.EXPIRED
        )


class Member(BaseModel):
    auth_user_id: int
    due_date: datetime
    member_type: MemberType | None
    cancelled: bool

    @property
    def status(self) -> MemberStatus:
        return MemberStatus.calc_expiry(self.due_date)

    @staticmethod
    def from_db_model(model: dbmodel.Member) -> Member:
        return Member(
            auth_user_id=model.auth_user_id,
            due_date=model.due_date,
            member_type=MemberType.from_db_model(model.member_type)
            if model.member_type is not None
            else None,
            cancelled=model.cancelled,
        )


class ReadMember(BaseModel):
    user_id: int
    due_date: datetime
    member_type: str | None
    status: MemberStatus
    cancelled: bool

    @staticmethod
    def from_member(member: Member) -> ReadMember:
        return ReadMember(
            user_id=member.auth_user_id,
            due_date=member.due_date,
            member_type=member.member_type.name
            if member.member_type is not None
            else None,
            status=member.status,
            cancelled=member.cancelled,
        )


class MemberType(BaseModel):
    id: UUID
    name: str
    price: int

    @staticmethod
    def from_db_model(model: dbmodel.MemberType) -> MemberType:
        return MemberType(
            id=model.id,
            name=model.name,
            price=model.price,
        )
