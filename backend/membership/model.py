from datetime import datetime
from uuid import UUID

from utils import BaseModel
from database import model as dbmodel
from database.types import MemberStatus


class Member(BaseModel):
    auth_user_id: int
    membership_expires: datetime
    member_type_id: UUID | None
    status: MemberStatus
    cancelled: bool

    @staticmethod
    def from_db_model(model: dbmodel.Member) -> Member:
        return Member(
            auth_user_id=model.auth_user_id,
            membership_expires=model.membership_expires,
            member_type_id=model.member_type_id,
            status=model.status,
            cancelled=model.cancelled,
        )


class ReadMember(BaseModel):
    auth_user_id: int
    membership_expires: datetime
    member_type_id: UUID | None
    status: MemberStatus
    cancelled: bool

    @staticmethod
    def from_member(member: Member) -> ReadMember:
        return ReadMember(
            auth_user_id=member.auth_user_id,
            membership_expires=member.membership_expires,
            member_type_id=member.member_type_id,
            status=member.status,
            cancelled=member.cancelled,
        )


class MembershipType(BaseModel):
    id: UUID
    name: str
    price: int

    @staticmethod
    def from_db_model(model: dbmodel.MemberType) -> MembershipType:
        return MembershipType(
            id=model.id,
            name=model.name,
            price=model.price,
        )
