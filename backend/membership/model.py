from datetime import datetime
from uuid import UUID

from utils import BaseModel
from database import model as dbmodel


class ReadMember(BaseModel):
    user_id: int
    due_date: datetime
    member_type: str | None
    active: bool
    cancelling: bool

    @staticmethod
    def from_db_model(model: dbmodel.Member) -> ReadMember:
        return ReadMember(
            user_id=model.user_id,
            due_date=model.due_date,
            member_type=model.member_type.name
            if model.member_type is not None
            else None,
            active=model.active,
            cancelling=model.cancelling,
        )


class ReadMemberType(BaseModel):
    id: UUID
    name: str
    price: int

    @staticmethod
    def from_db_model(model: dbmodel.MemberType) -> ReadMemberType:
        return ReadMemberType(
            id=model.id,
            name=model.name,
            price=model.price,
        )
