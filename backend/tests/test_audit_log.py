from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Callable

from audit_log.model import AuditPermissionCategory
from auth_module import PermissionTier, Permissions
import database.model as model


def test_permissions(test_server: TestClient, mock_get_session: Callable[[], Session]):
    with mock_get_session() as session:
        session.add(
            model.AuditLog(
                permission_category=AuditPermissionCategory.payments, log="1"
            )
        )
        session.add(
            model.AuditLog(permission_category=AuditPermissionCategory.mail, log="2")
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
                permission_category=AuditPermissionCategory.payments,
                log="1",
                time=datetime(2020, 1, 1),
            )
        )
        session.add(
            model.AuditLog(
                permission_category=AuditPermissionCategory.mail,
                log="2",
                time=datetime(2021, 1, 1),
            )
        )
        session.commit()
    response = test_server.get("/audit_log")
    assert len(response.json()) == 2

    response = test_server.get("/audit_log?before=2020-06-01")
    assert len(response.json()) == 1

    response = test_server.get("/audit_log?after=2020-06-01")
    assert len(response.json()) == 1

    response = test_server.get("/audit_log?before=2020-06-01")
    assert len(response.json()) == 1

    response = test_server.get("/audit_log?after=2020-06-01&before=2020-06-02")
    assert len(response.json()) == 0

    response = test_server.get("/audit_log?after=2019-12-31&before=2020-01-02")
    assert len(response.json()) == 1


def test_category_queries(
    test_server: TestClient, mock_get_session: Callable[[], Session]
):
    with mock_get_session() as session:
        session.add(
            model.AuditLog(
                permission_category=AuditPermissionCategory.payments,
                log="1",
                time=datetime(2020, 1, 1),
            )
        )
        session.add(
            model.AuditLog(
                permission_category=AuditPermissionCategory.mail,
                log="2",
                time=datetime(2021, 1, 1),
            )
        )
        session.commit()
    response = test_server.get("/audit_log")
    assert len(response.json()) == 2

    response = test_server.get("/audit_log?category=mail")
    assert len(response.json()) == 1

    response = test_server.get("/audit_log?category=mail&category=payments")
    assert len(response.json()) == 2

    response = test_server.get("/audit_log?category=invalid")
    assert response.status_code == 422  # "Unprocessable entity"

    # You can't query a category that you don't have permission for
    with mock_get_session() as session:
        session.get_one(model.AuthUser, 0).permissions = Permissions().model_dump_json()
        session.commit()

    response = test_server.get("/audit_log?category=mail&category=payments")
    assert response.status_code == 401
