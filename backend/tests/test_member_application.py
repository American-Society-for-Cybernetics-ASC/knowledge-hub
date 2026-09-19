from typing import Callable
from sqlalchemy.orm import Session
from database import model

from database.types import ApplicationStatus
from member_application.module import MemberApplicationModule
from fastapi.testclient import TestClient


def create_auth_user(get_session: Callable[[], Session], auth_user_id: int) -> int:
    with get_session() as session:
        auth_user = model.AuthUser(
            user_id=auth_user_id,
            name="User",
            email="member@gmail.com",
            permissions={"role": "member"},
        )

        session.add(auth_user)
        session.commit()
        session.refresh(auth_user)

        return auth_user.user_id


def create_application(
    get_session: Callable[[], Session],
    auth_user_id: int,
    content: str = "Test application",
) -> int:
    with get_session() as session:
        application = model.MembershipApplication(
            auth_user_id=auth_user_id,
            status=ApplicationStatus.PENDING,
            content=content,
        )
        session.add(application)
        session.commit()
        session.refresh(application)

        return application.application_id


def test_submit_application(mock_get_session):
    auth_user_id = 0

    application = MemberApplicationModule().submit_application(
        auth_user_id,
        "I want to join please",
    )

    assert application.application_id is not None
    assert application.auth_user_id == auth_user_id
    assert application.status == ApplicationStatus.PENDING
    assert application.submitted_at is not None
    assert application.content == "I want to join please"


def test_get_applications(mock_get_session):
    auth_user_id = create_auth_user(mock_get_session, 1)

    create_application(
        mock_get_session,
        auth_user_id,
        "user one",
    )

    create_application(
        mock_get_session,
        auth_user_id,
        "user two",
    )

    applications = MemberApplicationModule().get_all_applications()

    assert len(applications) == 2
    assert applications[0].content == "user one"
    assert applications[1].content == "user two"


def test_get_application(mock_get_session):
    auth_user_id = create_auth_user(mock_get_session, 1)

    application_id = create_application(
        mock_get_session, auth_user_id, "Test application"
    )

    application = MemberApplicationModule().get_application(application_id)

    assert application.application_id == application_id
    assert application.auth_user_id == auth_user_id
    assert application.status == ApplicationStatus.PENDING
    assert application.content == "Test application"


def test_revise_application(mock_get_session):
    auth_user_id = create_auth_user(mock_get_session, 1)

    application_id = create_application(
        mock_get_session, auth_user_id, "old application"
    )
    application = MemberApplicationModule().revise_application(
        application_id, auth_user_id, "new application"
    )

    assert application.application_id == application_id
    assert application.content == "new application"
    assert application.status == ApplicationStatus.PENDING


def test_approve_application(mock_get_session):
    auth_user_id = create_auth_user(mock_get_session, 1)

    application_id = create_application(
        mock_get_session, auth_user_id, "Test application"
    )

    application = MemberApplicationModule().approve_application(application_id)

    assert application.application_id == application_id
    assert application.status == ApplicationStatus.APPROVED


def test_deny_application(mock_get_session):
    auth_user_id = create_auth_user(mock_get_session, 1)

    application_id = create_application(
        mock_get_session, auth_user_id, "Test application"
    )

    application = MemberApplicationModule().deny_application(application_id)

    assert application.application_id == application_id
    assert application.status == ApplicationStatus.DENIED


def test_request_revision(mock_get_session):
    auth_user_id = create_auth_user(mock_get_session, 1)
    application_id = create_application(
        mock_get_session, auth_user_id, "Test application"
    )

    application = MemberApplicationModule().request_revision(application_id)

    assert application.application_id == application_id
    assert application.status == ApplicationStatus.REVISION_REQUIRED


def test_submit_application_api(test_server: TestClient, mock_get_session):
    """test submitting an application through the api"""
    auth_user_id = 0
    response = test_server.post(
        "/membership/application/", json={"content": "I want to join please"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["application_id"] is not None
    assert data["auth_user_id"] == auth_user_id
    assert data["status"] == "pending"
    assert data["content"] == ("I want to join please")
    assert data["submitted_at"] is not None


def test_get_applications_api(test_server: TestClient, mock_get_session):
    """test getting all applications through the api"""
    auth_user_id = create_auth_user(mock_get_session, 1)

    create_application(mock_get_session, auth_user_id, "application one")
    create_application(mock_get_session, auth_user_id, "application two")

    response = test_server.get("/membership/application/admin/all")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["content"] == "application one"
    assert data[1]["content"] == "application two"


def test_get_application_api(test_server: TestClient, mock_get_session):
    """Test getting one application through the api"""
    auth_user_id = create_auth_user(mock_get_session, 1)

    application_id = create_application(
        mock_get_session, auth_user_id, "Test application"
    )

    response = test_server.get(f"/membership/application/{application_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["application_id"] == application_id
    assert data["auth_user_id"] == auth_user_id
    assert data["status"] == "pending"
    assert data["content"] == "Test application"


def test_revise_application_api(test_server: TestClient, mock_get_session):
    """Test revising an application through the api"""
    auth_user_id = 0
    application_id = create_application(
        mock_get_session, auth_user_id, "old application"
    )
    response = test_server.patch(
        f"/membership/application/{application_id}", json={"content": "new application"}
    )
    assert response.status_code == 200

    data = response.json()

    assert data["application_id"] == application_id
    assert data["content"] == "new application"
    assert data["status"] == "pending"


def test_approve_application_api(test_server: TestClient, mock_get_session):
    """Test approving an application through the api"""
    auth_user_id = create_auth_user(mock_get_session, 1)
    application_id = create_application(
        mock_get_session, auth_user_id, "Test application"
    )

    response = test_server.post(f"/membership/application/{application_id}/approve")

    assert response.status_code == 200
    data = response.json()

    assert data["application_id"] == application_id
    assert data["status"] == "approved"


def test_deny_application_api(test_server: TestClient, mock_get_session):
    """Test denying an application through the api"""
    auth_user_id = create_auth_user(mock_get_session, 1)
    application_id = create_application(
        mock_get_session, auth_user_id, "Test application"
    )
    response = test_server.post(f"/membership/application/{application_id}/deny")
    assert response.status_code == 200
    data = response.json()

    assert data["application_id"] == application_id
    assert data["status"] == "denied"


def test_request_revision_api(test_server: TestClient, mock_get_session):
    """Test requesting a revision through the api"""
    auth_user_id = create_auth_user(mock_get_session, 1)
    application_id = create_application(
        mock_get_session, auth_user_id, "Test application"
    )

    response = test_server.post(
        f"/membership/application/{application_id}/request-revision"
    )

    assert response.status_code == 200
    data = response.json()

    assert data["application_id"] == application_id
    assert data["status"] == "revision_required"


def test_get_application_not_found_api(test_server: TestClient):
    """Test an application cannot be found and returns 404"""
    response = test_server.get("/membership/application/99999")

    assert response.status_code == 404
