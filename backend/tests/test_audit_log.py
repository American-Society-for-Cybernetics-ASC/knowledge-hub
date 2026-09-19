from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Callable

from audit_log.model import PermissionCategory
from auth_module import PermissionTier, Permissions
import database.model as model


def test_permissions(test_server: TestClient, mock_get_session: Callable[[], Session]):
    with mock_get_session() as session:
        session.add(
            model.AuditLog(permission_category=PermissionCategory.PAYMENT, log="1")
        )
        session.add(
            model.AuditLog(permission_category=PermissionCategory.MAIL, log="2")
        )
        session.get_one(model.AuthUser, 0).permissions = Permissions(
            tier=PermissionTier.adminstrator
        ).model_dump_json()
        session.commit()

    response = test_server.get("/audit_log")
    assert response.status_code == 200
    response = response.json()
    assert isinstance(response, list)
    assert len(response) == 2

    with mock_get_session() as session:
        session.get_one(model.AuthUser, 0).permissions = Permissions(
            children={"mail": Permissions(tier=PermissionTier.manager)}
        ).model_dump_json()
        session.commit()

    response = test_server.get("/audit_log")
    assert response.status_code == 200
    response = response.json()
    assert isinstance(response, list)
    assert len(response) == 1


def test_time_queries(test_server: TestClient, mock_get_session: Callable[[], Session]):
    with mock_get_session() as session:
        session.add(
            model.AuditLog(
                permission_category=PermissionCategory.PAYMENT,
                log="1",
                time=datetime(2020, 1, 1, tzinfo=timezone.utc),
            )
        )
        session.add(
            model.AuditLog(
                permission_category=PermissionCategory.MAIL,
                log="2",
                time=datetime(2021, 1, 1, tzinfo=timezone.utc),
            )
        )
        session.commit()

    # --- Reject timezoneless data ---
    response = test_server.get("/audit_log?before=2020-06-01T00:00:00")
    assert response.status_code == 400

    response = test_server.get("/audit_log?after=2020-06-01T00:00:00")
    assert response.status_code == 400

    # --- Accept valid requests, and respond correctly ---
    response = test_server.get("/audit_log")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = test_server.get("/audit_log?before=2020-06-01T00:00:00Z")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = test_server.get("/audit_log?after=2020-06-01T00:00:00Z")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = test_server.get("/audit_log?before=2020-06-01T00:00:00Z")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = test_server.get(
        "/audit_log?after=2020-06-01T00:00:00Z&before=2020-06-02T00:00:00Z"
    )
    assert response.status_code == 200
    assert len(response.json()) == 0

    response = test_server.get(
        "/audit_log?after=2019-12-31T00:00:00Z&before=2020-01-02T00:00:00Z"
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_category_queries(
    test_server: TestClient, mock_get_session: Callable[[], Session]
):
    with mock_get_session() as session:
        session.add(
            model.AuditLog(
                permission_category=PermissionCategory.PAYMENT,
                log="1",
                time=datetime(2020, 1, 1, tzinfo=timezone.utc),
            )
        )
        session.add(
            model.AuditLog(
                permission_category=PermissionCategory.MAIL,
                log="2",
                time=datetime(2021, 1, 1, tzinfo=timezone.utc),
            )
        )
        session.commit()
    response = test_server.get("/audit_log")
    assert len(response.json()) == 2

    response = test_server.get(f"/audit_log?category={PermissionCategory.MAIL.value}")
    assert len(response.json()) == 1

    response = test_server.get(
        f"/audit_log?category={PermissionCategory.MAIL.value}&category={PermissionCategory.PAYMENT.value}"
    )
    assert len(response.json()) == 2

    response = test_server.get("/audit_log?category=invalid")
    assert response.status_code == 422  # "Unprocessable entity"

    # You can't query a category that you don't have permission for
    with mock_get_session() as session:
        session.get_one(model.AuthUser, 0).permissions = Permissions().model_dump_json()
        session.commit()

    response = test_server.get(
        f"/audit_log?category={PermissionCategory.MAIL.value}&category={PermissionCategory.PAYMENT.value}"
    )
    assert response.status_code == 401
