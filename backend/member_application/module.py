from sqlalchemy import select
from database import model
import database
from member_application.model import MemberApplication, ApplicationStatus
from datetime import datetime, timezone


class ApplicationNotFoundError(Exception):
    """Raised when a member application cannot be found"""

    pass


class ApplicationNotOwnedError(Exception):
    """raised when a user tries to modify another user's application"""

    pass


class MemberApplicationModule:
    def get_applications(self) -> list[MemberApplication]:
        """returns a list of all member applications"""
        with database.get_session() as session:
            applications = (
                session.execute(select(model.MembershipApplication)).scalars().all()
            )
            return [
                MemberApplication.model_validate_sqlalchemy(application)
                for application in applications
            ]

    def get_application(self, application_id: int) -> MemberApplication:
        """returns a single member applicaiton"""
        with database.get_session() as session:
            application = session.get(model.MembershipApplication, application_id)

            if application is None:
                raise ApplicationNotFoundError(
                    f"Application for member {application_id} cannot be found"
                )
            return MemberApplication.model_validate_sqlalchemy(application)

    def submit_application(self, auth_user_id: int, content: str) -> MemberApplication:
        """Submit a new member application"""
        with database.get_session() as session:
            application = model.MembershipApplication(
                auth_user_id=auth_user_id,
                status=ApplicationStatus.PENDING,
                submitted_at=datetime.now(timezone.utc),
                content=content,
            )
            session.add(application)
            session.commit()

            return MemberApplication.model_validate_sqlalchemy(application)

    def revise_application(
        self, application_id: int, auth_user_id: int, content: str
    ) -> MemberApplication:
        """revise an existing member application"""
        with database.get_session() as session:
            application = session.get(model.MembershipApplication, application_id)

            if application is None:
                raise ApplicationNotFoundError(
                    f"Application for member {application_id} cannot be found"
                )

            if application.auth_user_id != auth_user_id:
                raise ApplicationNotOwnedError("You do not own this application")

            application.content = content
            application.status = ApplicationStatus.PENDING

            session.commit()
            return MemberApplication.model_validate_sqlalchemy(application)

    def approve_application(self, application_id: int) -> MemberApplication:
        """approve a member application"""
        with database.get_session() as session:
            application = session.get(model.MembershipApplication, application_id)

            if application is None:
                raise ApplicationNotFoundError(
                    f"Application for member {application_id} cannot be found"
                )
            application.status = ApplicationStatus.APPROVED
            session.commit()
            return MemberApplication.model_validate_sqlalchemy(application)

    def deny_application(self, application_id: int) -> MemberApplication:
        """deny a member application"""
        with database.get_session() as session:
            application = session.get(model.MembershipApplication, application_id)

            if application is None:
                raise ApplicationNotFoundError(
                    f"Application for meember {application_id} not found"
                )

            application.status = ApplicationStatus.DENIED
            session.commit()

            return MemberApplication.model_validate_sqlalchemy(application)

    def request_revision(self, application_id: int) -> MemberApplication:
        """request a revision for a member application"""
        with database.get_session() as session:
            application = session.get(model.MembershipApplication, application_id)
            if application is None:
                raise ApplicationNotFoundError(
                    f"Application for member {application_id} cannot be found"
                )
            application.status = ApplicationStatus.REVISION_REQUIRED
            session.commit()
            return MemberApplication.model_validate_sqlalchemy(application)
