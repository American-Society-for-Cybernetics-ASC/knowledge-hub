import datetime
from uuid import UUID

from fastapi.testclient import TestClient
import pytest

from database.module_configs import MembershipsConfig
from utils.module_config import get_module_config
from database.types import ApplicationStatus
from .conftest import TEST_USER_ID
from database import model as dbmodel


@pytest.fixture()
def mock_application(mock_get_session, mock_member_type) -> int:
    with mock_get_session() as session:
        application = dbmodel.MembershipApplication(
            user_id=TEST_USER_ID,
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
            user_id=TEST_USER_ID,
            due_date=datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=10),
            member_type_id=None,
        )
        session.add(member)
        session.commit()
        session.refresh(member)
        return member.user_id


def test_full_cycle(
    mock_payment_provider: UUID, mock_application: int, test_server: TestClient
):
    response = test_server.get("/membership")
    assert response.status_code == 200
    assert response.json() is None  # Not a member

    response = test_server.post(
        "/membership/purchase", json={"application_id": mock_application}
    )
    assert response.status_code == 200, f"{response.content.decode()}"
    payment = response.json()

    response = test_server.post(
        "/payments/transactions",
        json={"provider_id": str(mock_payment_provider), "payment_id": payment["id"]},
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
    assert not response.json()["cancelling"]

    test_server.post("/membership/cancel")
    assert response.status_code == 200

    response = test_server.get("/membership")
    assert response.status_code == 200
    assert response.json()["cancelling"]

    test_server.post("/membership/uncancel")
    assert response.status_code == 200

    response = test_server.get("/membership")
    assert response.status_code == 200
    assert not response.json()["cancelling"]


def test_update(test_server: TestClient, mock_member, mock_application):
    response = test_server.get("/membership")
    assert response.status_code == 200
    assert response.json()["member_type"] is None

    response = test_server.post(
        "/membership/update", json={"application_id": mock_application}
    )
    assert response.status_code == 200

    response = test_server.get("/membership")
    assert response.status_code == 200
    assert response.json()["member_type"] is not None


def test_renew(
    test_server: TestClient, mock_member, mock_application, mock_payment_provider
):
    response = test_server.get("/membership")
    assert response.status_code == 200
    assert response.json()["member_type"] is None
    current_membership_duration = response.json()["due_date"]

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
        json={"provider_id": str(mock_payment_provider), "payment_id": payment["id"]},
    )
    assert response.status_code == 200
    transaction = response.json()

    response = test_server.post(
        f"/payments/transactions/{transaction['id']}/confirm",
    )
    assert response.status_code == 200

    response = test_server.get("/membership")
    assert response.status_code == 200
    assert response.json()["due_date"] > current_membership_duration


def test_dues_notifications(
    test_server: TestClient,
    monkeypatch,
    mock_get_session,
    mock_mail_manager,
    mock_mail_provider,
):
    with mock_get_session() as session:
        config = get_module_config(session, MembershipsConfig)
        config.email_provider_id = mock_mail_provider

        member = dbmodel.Member(
            user_id=TEST_USER_ID,
            due_date=datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=365),
            member_type_id=None,
        )
        session.add(member)

        session.commit()

    time = datetime.datetime.now(datetime.timezone.utc)

    with monkeypatch.context() as m:
        m.setattr(
            "cron.cron_module._now",
            lambda: time,
        )
        m.setattr(
            "membership.membership_module._now",
            lambda: time,
        )

        r = test_server.get("cron")
        assert r.status_code == 200
        assert len(mock_mail_manager.sent_mail()) == 0

        time += datetime.timedelta(days=336)
        r = test_server.get("cron")
        assert r.status_code == 200
        assert len(mock_mail_manager.sent_mail()) == 1

        r = test_server.get("cron")
        assert r.status_code == 200
        assert len(mock_mail_manager.sent_mail()) == 1

        time += datetime.timedelta(days=30)
        r = test_server.get("cron")
        assert r.status_code == 200
        assert len(mock_mail_manager.sent_mail()) == 2
        r = test_server.get("cron")
        assert r.status_code == 200
        assert len(mock_mail_manager.sent_mail()) == 2

        time += datetime.timedelta(days=22)
        r = test_server.get("cron")
        assert r.status_code == 200
        assert len(mock_mail_manager.sent_mail()) == 3
        r = test_server.get("cron")
        assert r.status_code == 200
        assert len(mock_mail_manager.sent_mail()) == 3
