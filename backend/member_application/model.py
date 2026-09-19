from datetime import datetime

from membership.model import MemberType
from database.types import ApplicationStatus
from database import model as dbmodel
from utils import BaseModel


class MembershipApplication(BaseModel):
    application_id: int
    auth_user_id: int
    member_type: MemberType | None
    status: ApplicationStatus
    submitted_at: datetime
    content: str

    @staticmethod
    def from_db_model(
        model: dbmodel.MembershipApplication,
    ) -> MembershipApplication:
        return MembershipApplication(
            application_id=model.application_id,
            auth_user_id=model.auth_user_id,
            member_type=MemberType.from_db_model(model.member_type)
            if model.member_type is not None
            else None,
            status=model.status,
            submitted_at=model.submitted_at,
            content=model.content,
        )
