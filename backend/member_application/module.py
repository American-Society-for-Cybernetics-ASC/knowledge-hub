from uuid import UUID

from sqlalchemy import desc, select
from datetime import datetime, timezone

from database.types import ApplicationStatus
from database import model as dbmodel
import database
from .model import MembershipApplication


class ApplicationNotFoundError(Exception):
    """Raised when a member application cannot be found"""

    pass


class ApplicationNotOwnedError(Exception):
    """raised when a user tries to modify another user's application"""

    pass


class ApplicationCompleteError(Exception):
    """raised when a user tries to edit a completed application"""

    pass


class MemberApplicationModule:
    def get_users_applications(self, user_id: int) -> list[MembershipApplication]:
        """returns a list of all member applications"""
        with database.get_session() as session:
            return list(
                map(
                    MembershipApplication.from_db_model,
                    session.execute(
                        select(dbmodel.MembershipApplication)
                        .where(dbmodel.MembershipApplication.auth_user_id == user_id)
                        .order_by(desc(dbmodel.MembershipApplication.last_edited))
                    )
                    .scalars()
                    .all(),
                )
            )

    def get_all_applications(self) -> list[MembershipApplication]:
        """returns a list of all member applications"""
        with database.get_session() as session:
            return list(
                map(
                    MembershipApplication.from_db_model,
                    session.execute(select(dbmodel.MembershipApplication))
                    .scalars()
                    .all(),
                )
            )

    def get_application(self, application_id: int) -> MembershipApplication:
        """returns a single member applicaiton"""
        with database.get_session() as session:
            application = session.get(dbmodel.MembershipApplication, application_id)

            if application is None:
                raise ApplicationNotFoundError(
                    f"Application for member {application_id} cannot be found"
                )
            return MembershipApplication.from_db_model(application)

    def submit_application(
        self,
        auth_user_id: int,
        content: str,
        member_type_id: UUID,
    ) -> MembershipApplication:
        """Submit a new member application"""
        with database.get_session() as session:
            application = dbmodel.MembershipApplication(
                auth_user_id=auth_user_id,
                status=ApplicationStatus.PENDING,
                member_type_id=member_type_id,
                submitted_at=datetime.now(timezone.utc),
                content=content,
            )
            session.add(application)
            session.commit()

            return MembershipApplication.from_db_model(application)

    def revise_application(
        self, application_id: int, auth_user_id: int, content: str
    ) -> MembershipApplication:
        """revise an existing member application"""
        with database.get_session() as session:
            application = session.get(dbmodel.MembershipApplication, application_id)

            if application is None:
                raise ApplicationNotFoundError(
                    f"Application for member {application_id} cannot be found"
                )

            if application.auth_user_id != auth_user_id:
                raise ApplicationNotOwnedError("You do not own this application")

            if application.status not in [
                ApplicationStatus.PENDING,
                ApplicationStatus.REVISION_REQUIRED,
            ]:
                raise ApplicationCompleteError(
                    "This application is not in a state to be edited."
                )

            application.content = content
            application.status = ApplicationStatus.PENDING
            application.last_edited = datetime.now(timezone.utc)

            session.commit()
            return MembershipApplication.from_db_model(application)

    def approve_application(self, application_id: int) -> MembershipApplication:
        """approve a member application"""
        with database.get_session() as session:
            application = session.get(dbmodel.MembershipApplication, application_id)

            if application is None:
                raise ApplicationNotFoundError(
                    f"Application for member {application_id} cannot be found"
                )
            application.status = ApplicationStatus.APPROVED
            session.commit()
            return MembershipApplication.from_db_model(application)

    def deny_application(self, application_id: int) -> MembershipApplication:
        """deny a member application"""
        with database.get_session() as session:
            application = session.get(dbmodel.MembershipApplication, application_id)

            if application is None:
                raise ApplicationNotFoundError(
                    f"Application for meember {application_id} not found"
                )

            application.status = ApplicationStatus.DENIED
            session.commit()

            return MembershipApplication.from_db_model(application)

    def request_revision(self, application_id: int) -> MembershipApplication:
        """request a revision for a member application"""
        with database.get_session() as session:
            application = session.get(dbmodel.MembershipApplication, application_id)
            if application is None:
                raise ApplicationNotFoundError(
                    f"Application for member {application_id} cannot be found"
                )
            application.status = ApplicationStatus.REVISION_REQUIRED
            session.commit()
            return MembershipApplication.from_db_model(application)
