from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from database.model import MembershipApplication
from database.types import ApplicationStatus


class ApplicationNotFoundError(Exception):
    """Raised when a member application cannot be found"""

    pass


class ApplicationNotOwnedError(Exception):
    """raised when a user tries to modify another user's application"""

    pass


class ApplicationCompleteError(Exception):
    """raised when a user tries to edit a completed application"""

    pass


def get_application(session: Session, application_id: int) -> MembershipApplication:
    """
    :raises ApplicationNotFoundError:
    """
    application = session.get(MembershipApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(
            f"Application for member {application_id} cannot be found"
        )
    return application


def get_users_applications(
    session: Session, user_id: int
) -> list[MembershipApplication]:
    """returns a list of all member applications"""
    return list(
        session.execute(
            select(MembershipApplication)
            .where(MembershipApplication.user_id == user_id)
            .order_by(desc(MembershipApplication.last_edited))
        )
        .scalars()
        .all(),
    )


def get_all_applications(session: Session) -> list[MembershipApplication]:
    """returns a list of all member applications"""
    return list(
        session.execute(select(MembershipApplication)).scalars().all(),
    )


def submit_application(
    session: Session,
    user_id: int,
    content: str,
    member_type_id: UUID,
) -> MembershipApplication:
    """Submit a new member application"""
    with session.begin_nested():
        application = MembershipApplication(
            user_id=user_id,
            status=ApplicationStatus.PENDING,
            member_type_id=member_type_id,
            submitted_at=datetime.now(timezone.utc),
            content=content,
        )
        session.add(application)
    return application


def revise_application(
    session: Session, application_id: int, user_id: int, content: str
) -> MembershipApplication:
    """
    revise an existing member application

    :raises ApplicationNotFounderror:
    :raises ApplicationNotOwnedError:
    :raises ApplicationCompleteError:
    """
    application = get_application(session, application_id)

    if application.user_id != user_id:
        raise ApplicationNotOwnedError("You do not own this application")

    if application.status not in [
        ApplicationStatus.PENDING,
        ApplicationStatus.REVISION_REQUIRED,
    ]:
        raise ApplicationCompleteError(
            "This application is not in a state to be edited."
        )

    with session.begin_nested():
        application.content = content
        application.status = ApplicationStatus.PENDING
        application.last_edited = datetime.now(timezone.utc)

    return application


def approve_application(session: Session, application_id: int) -> MembershipApplication:
    """
    approve a member application

    :raises ApplicationNotFoundError:
    """
    application = get_application(session, application_id)

    with session.begin_nested():
        application.status = ApplicationStatus.APPROVED

    return application


def deny_application(session: Session, application_id: int) -> MembershipApplication:
    """
    deny a member application

    :raises ApplicationNotFoundError:
    """
    application = get_application(session, application_id)

    with session.begin_nested():
        application.status = ApplicationStatus.DENIED

    return application


def request_revision(session: Session, application_id: int) -> MembershipApplication:
    """
    request a revision for a member application

    :raises ApplicationNotFoundError:
    """
    application = get_application(session, application_id)

    with session.begin_nested():
        application.status = ApplicationStatus.REVISION_REQUIRED

    return application
