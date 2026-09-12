import datetime
from uuid import UUID

from fastapi.testclient import TestClient
import pytest
from .conftest import TEST_USER_ID
from member_application.model import ApplicationStatus
from database import model as dbmodel


@pytest.fixture()
def mock_member_type(mock_get_session) -> UUID:
    with mock_get_session() as session:
        member_type = dbmodel.MemberType(name="ExampleType", price=10_000)
        session.add(member_type)
        session.commit()
        session.refresh(member_type)
        return member_type.id


@pytest.fixture()
def mock_application(mock_get_session, mock_member_type) -> int:
    with mock_get_session() as session:
        application = dbmodel.MembershipApplication(
            auth_user_id=TEST_USER_ID,
            member_type_id=mock_member_type,
            status=ApplicationStatus.APPROVED,
            content="example application",
        )
        session.add(application)
        session.commit()
        session.refresh(application)
        return application.application_id


@pytest.fixture()
def mock_member(mock_get_session) -> int:
    with mock_get_session() as session:
        member = dbmodel.Member(
            auth_user_id=TEST_USER_ID,
            membership_expires=datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=10),
            cancelled=False,
            member_type_id=None,
        )
        session.add(member)
        session.commit()
        session.refresh(member)
        return member.auth_user_id


def test_full_cycle(
    mock_provider: UUID, mock_application: int, test_server: TestClient
):
    response = test_server.get("/membership")
    assert response.status_code == 400  # Not a member

    response = test_server.post(
        "/membership/purchase", json={"application_id": mock_application}
    )
    assert response.status_code == 200, f"{response.content.decode()}"
    payment = response.json()

    response = test_server.post(
        "/payments/transactions",
        json={"provider_id": str(mock_provider), "payment_id": payment["id"]},
    )
    assert response.status_code == 200
    transaction = response.json()

    response = test_server.post(
        f"/payments/transactions/{transaction['id']}/confirm",
    )
    assert response.status_code == 200

    response = test_server.get("/membership")
    assert response.status_code == 200  # Now a member


def test_cancel(test_server: TestClient, mock_member):
    response = test_server.get("/membership")
    assert response.status_code == 200
    assert not response.json()["cancelled"]

    test_server.post("/membership/cancel")
    assert response.status_code == 200

    response = test_server.get("/membership")
    assert response.status_code == 200
    assert response.json()["cancelled"]

    test_server.post("/membership/uncancel")
    assert response.status_code == 200

    response = test_server.get("/membership")
    assert response.status_code == 200
    assert not response.json()["cancelled"]


def test_update(test_server: TestClient, mock_member, mock_application):
    response = test_server.get("/membership")
    assert response.status_code == 200
    assert response.json()["member_type_id"] is None

    response = test_server.post(
        "/membership/update", json={"application_id": mock_application}
    )
    assert response.status_code == 200

    response = test_server.get("/membership")
    assert response.status_code == 200
    assert response.json()["member_type_id"] is not None


def test_renew(test_server: TestClient, mock_member, mock_application, mock_provider):
    response = test_server.get("/membership")
    assert response.status_code == 200
    assert response.json()["member_type_id"] is None
    current_membership_duration = response.json()["membership_expires"]

    # Not currently renewable
    response = test_server.post("/membership/renew")
    assert response.status_code == 400

    # Update member_type
    response = test_server.post(
        "/membership/update", json={"application_id": mock_application}
    )
    assert response.status_code == 200

    # Successfully create the payment
    response = test_server.post("/membership/renew")
    assert response.status_code == 200
    payment = response.json()

    response = test_server.post(
        "/payments/transactions",
        json={"provider_id": str(mock_provider), "payment_id": payment["id"]},
    )
    assert response.status_code == 200
    transaction = response.json()

    response = test_server.post(
        f"/payments/transactions/{transaction['id']}/confirm",
    )
    assert response.status_code == 200

    response = test_server.get("/membership")
    assert response.status_code == 200
    assert response.json()["membership_expires"] > current_membership_duration
