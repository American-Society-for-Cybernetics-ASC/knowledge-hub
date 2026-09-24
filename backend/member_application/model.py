from datetime import datetime

from membership.model import ReadMemberType
from database.types import ApplicationStatus
from database import model as dbmodel
from utils import BaseModel


class MembershipApplication(BaseModel):
    application_id: int
    user_id: int
    member_type: ReadMemberType | None
    status: ApplicationStatus
    submitted_at: datetime
    last_edited: datetime
    content: str

    @staticmethod
    def from_db_model(
        model: dbmodel.MembershipApplication,
    ) -> MembershipApplication:
        return MembershipApplication(
            application_id=model.application_id,
            user_id=model.user_id,
            member_type=ReadMemberType.from_db_model(model.member_type)
            if model.member_type is not None
            else None,
            status=model.status,
            submitted_at=model.submitted_at,
            last_edited=model.last_edited,
            content=model.content,
        )
