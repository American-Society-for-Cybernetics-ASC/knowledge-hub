from typing import Callable
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import model
from member_application.module import MemberApplicationModule
from member_application.model import ApplicationStatus

def create_member(get_session: Callable[[], Session]) -> int:
    with get_session() as session:
        auth_user = model.AuthUser(
            name="User",
            email="member@gmail.com",
            permission={"role": "member"},
        )
        session.add(auth_user)
        session.flush()

        member = model.Member(status="active", auth_user_id=auth_user.user_id)
        session.add(member)
        session.commit()
        session.refresh(member)

        return member.member_id

def create_application(
        get_session: Callable[[], Session],
        member_id: int,
        content: dict | None = None,
) -> int:
    with get_session() as session:
        application = model.MembershipApplication(
            member_id=member_id,
            status=ApplicationStatus.PENDING,
            content=content or {"name": "Test User"},
        )
        session.add(application)
        session.commit()
        session.refresh(application)

        return application.application_id

def test_submit_application(mock_get_session):
    member_id = create_member(mock_get_session)

    application = MemberApplicationModule().submit_application(
        member_id,
        {"name": "Test User", "reason": "I want to join please"},
    )

    assert application.application_id is not None
    assert application.member_id == member_id
    assert application.status == ApplicationStatus.PENDING
    assert application.submitted_at is not None
    assert application.content == {"name": "Test User", "reason": "I want to join please"}

def test_get_applications(mock_get_session):
    member_id = create_member(mock_get_session)

    create_application(
        mock_get_session,
        member_id,
        {"name": "User One"},
    )

    create_application(
        mock_get_session,
        member_id,
        {"name": "User Two"}
    )

    applications = MemberApplicationModule().get_applications()

    assert len(applications) == 2
    assert applications[0].content == {"name": "User One"}
    assert applications[1].content == {"name": "User Two"}

def get_application(mock_get_session):
    member_id = create_member(mock_get_session)

    application_id = create_application(mock_get_session, member_id, {"name": "Test User"})

    application = MemberApplicationModule().get_application(application_id)

    assert application.application_id == application_id
    assert application.member_id == member_id
    assert application.status == ApplicationStatus.PENDING
    assert application.content == {"name": "Test User"}

def test_revise_application(mock_get_session):
    member_id = create_member(mock_get_session)

    application_id = create_application(
        mock_get_session,
        member_id,
        {"name": "Old Name"},
    )
    application = MemberApplicationModule().revise_application(application_id, {"name": "New Name"})

    assert application.application_id == application_id
    assert application.content == {"name": "New Name"}
    assert application.status == ApplicationStatus.PENDING

def test_approve_application(mock_get_session):
    member_id = create_member(mock_get_session)

    application_id = create_application(mock_get_session, member_id)

    application = MemberApplicationModule().approve_application(application_id)

    assert application.application_id == application_id
    assert application.status == ApplicationStatus.APPROVED

def test_deny_application(mock_get_session):
    member_id = create_member(mock_get_session)

    application_id = create_application(mock_get_session, member_id)

    application = MemberApplicationModule().deny_application(application_id)

    assert application.application_id == application_id
    assert application.status == ApplicationStatus.DENIED

def test_request_revision(mock_get_session):
    member_id = create_member(mock_get_session)
    application_id = create_application(mock_get_session, member_id)

    application = MemberApplicationModule().request_revision(application_id)

    assert application.application_id == application_id
    assert application.status == ApplicationStatus.REVISION_REQUIRED