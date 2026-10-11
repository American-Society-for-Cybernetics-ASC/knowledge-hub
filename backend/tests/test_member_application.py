from datetime import datetime
from typing import Callable
from sqlalchemy.orm import Session
from database import model

from database.types import ApplicationStatus
from member_application import application_module
from fastapi.testclient import TestClient


def create_auth_user(get_session: Callable[[], Session], user_id: int) -> int:
    with get_session() as session:
        auth_user = model.AuthUser(
            user_id=user_id,
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
    user_id: int,
    content: str = "Test application",
    status: ApplicationStatus = ApplicationStatus.PENDING,
) -> model.MembershipApplication:
    with get_session() as session:
        application = model.MembershipApplication(
            user_id=user_id,
            status=status,
            content=content,
        )
        session.add(application)
        session.commit()
        session.refresh(application)

        return application


def test_submit_application(mock_get_session, mock_member_type):
    user_id = 0

    with mock_get_session() as session:
        application = application_module.submit_application(
            session, user_id, "I want to join please", mock_member_type
        )

    assert application.application_id is not None
    assert application.user_id == user_id
    assert application.status == ApplicationStatus.PENDING
    assert application.last_edited is not None
    assert application.content == "I want to join please"


def test_get_applications(mock_get_session):
    user_id = create_auth_user(mock_get_session, 1)

    create_application(
        mock_get_session,
        user_id,
        "user one",
    )

    create_application(
        mock_get_session,
        user_id,
        "user two",
    )

    with mock_get_session() as session:
        applications = application_module.get_all_applications(session)

    assert len(applications) == 2
    assert applications[0].content == "user one"
    assert applications[1].content == "user two"


def test_get_application(mock_get_session):
    user_id = create_auth_user(mock_get_session, 1)

    application_id = create_application(
        mock_get_session, user_id, "Test application"
    ).application_id

    with mock_get_session() as session:
        application = application_module.get_application(session, application_id)

    assert application.application_id == application_id
    assert application.user_id == user_id
    assert application.status == ApplicationStatus.PENDING
    assert application.content == "Test application"


def test_revise_application(mock_get_session):
    user_id = create_auth_user(mock_get_session, 1)

    application_id = create_application(
        mock_get_session, user_id, "old application"
    ).application_id
    with mock_get_session() as session:
        application = application_module.revise_application(
            session, application_id, user_id, "new application"
        )

    assert application.application_id == application_id
    assert application.content == "new application"
    assert application.status == ApplicationStatus.PENDING


def test_approve_application(mock_get_session):
    user_id = create_auth_user(mock_get_session, 1)

    application_id = create_application(
        mock_get_session, user_id, "Test application"
    ).application_id

    with mock_get_session() as session:
        application = application_module.approve_application(session, application_id)

    assert application.application_id == application_id
    assert application.status == ApplicationStatus.APPROVED


def test_deny_application(mock_get_session):
    user_id = create_auth_user(mock_get_session, 1)

    application_id = create_application(
        mock_get_session, user_id, "Test application"
    ).application_id

    with mock_get_session() as session:
        application = application_module.deny_application(session, application_id)

    assert application.application_id == application_id
    assert application.status == ApplicationStatus.DENIED


def test_request_revision(mock_get_session):
    user_id = create_auth_user(mock_get_session, 1)
    application_id = create_application(
        mock_get_session, user_id, "Test application"
    ).application_id

    with mock_get_session() as session:
        application = application_module.request_revision(session, application_id)

    assert application.application_id == application_id
    assert application.status == ApplicationStatus.REVISION_REQUIRED


def test_submit_application_api(
    test_server: TestClient, mock_get_session, mock_member_type
):
    """test submitting an application through the api"""
    user_id = 0
    response = test_server.post(
        "/membership/application/",
        json={
            "content": "I want to join please",
            "member_type_id": str(mock_member_type),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["application_id"] is not None
    assert data["user_id"] == user_id
    assert data["status"] == "pending"
    assert data["content"] == ("I want to join please")
    assert data["submitted_at"] is not None


def test_get_applications_api(test_server: TestClient, mock_get_session):
    """test getting all applications through the api"""
    user_id = create_auth_user(mock_get_session, 1)

    create_application(mock_get_session, user_id, "application one")
    create_application(mock_get_session, user_id, "application two")

    response = test_server.get("/membership/application/admin/all")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["content"] == "application one"
    assert data[1]["content"] == "application two"


def test_get_application_api(test_server: TestClient, mock_get_session):
    """Test getting one application through the api"""
    user_id = create_auth_user(mock_get_session, 1)

    application_id = create_application(
        mock_get_session, user_id, "Test application"
    ).application_id

    response = test_server.get(f"/membership/application/{application_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["application_id"] == application_id
    assert data["user_id"] == user_id
    assert data["status"] == "pending"
    assert data["content"] == "Test application"


def test_revise_application_api(test_server: TestClient, mock_get_session):
    """Test revising an application through the api"""
    user_id = 0
    application_id = create_application(
        mock_get_session, user_id, "old application"
    ).application_id
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
    user_id = create_auth_user(mock_get_session, 1)
    application_id = create_application(
        mock_get_session, user_id, "Test application"
    ).application_id

    response = test_server.post(f"/membership/application/{application_id}/approve")

    assert response.status_code == 200
    data = response.json()

    assert data["application_id"] == application_id
    assert data["status"] == "approved"


def test_deny_application_api(test_server: TestClient, mock_get_session):
    """Test denying an application through the api"""
    user_id = create_auth_user(mock_get_session, 1)
    application_id = create_application(
        mock_get_session, user_id, "Test application"
    ).application_id
    response = test_server.post(f"/membership/application/{application_id}/deny")
    assert response.status_code == 200
    data = response.json()

    assert data["application_id"] == application_id
    assert data["status"] == "denied"


def test_request_revision_api(test_server: TestClient, mock_get_session):
    """Test requesting a revision through the api"""
    user_id = create_auth_user(mock_get_session, 1)
    application_id = create_application(
        mock_get_session, user_id, "Test application"
    ).application_id

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


def test_admin_get_applications_summary(test_server: TestClient, mock_get_session):
    """Test an application cannot be found and returns 404"""
    user_id = create_auth_user(mock_get_session, 1)
    create_application(mock_get_session, user_id, "Test application")
    create_application(mock_get_session, user_id, "Test application")
    last = create_application(mock_get_session, user_id, "Test application")
    create_application(
        mock_get_session, user_id, "Test application", ApplicationStatus.DENIED
    )

    response = test_server.get("/membership/application/admin/summary")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert (
        datetime.fromisoformat(response.json()[0]["last_application"])
        == last.last_edited
    )
