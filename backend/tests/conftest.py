# Define global fixtures

# Stops us from running startup scripts
from pytest import MonkeyPatch
from settings import SETTINGS

with MonkeyPatch().context() as m:
    m.setattr(SETTINGS, "testing", True)
    from main import app

from typing import Callable
import uuid

from mail.model import Email
from payments.config import PaymentModuleConfig, PaymentOption
from payments.providers.mock_provider import MockPaymentProvider
from utils.module_config import set_module_config
from .mock_mail_provider import MockMailProvider
import database
from database import model
from database.base import Base
import auth_module


import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture
def test_server() -> TestClient:
    """Returns a TestClient around the app from main.py"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    """Override settings as needed for tests"""
    with monkeypatch.context() as m:
        m.setattr(SETTINGS, "testing", True)
        m.setattr(
            SETTINGS,
            "secret_key",
            """
MIIEpAIBAAKCAQEAx6Leb7pGwWXHnSPMPZmfoSX4W4F5I98QNqP3FH3FH4xPgH8O
X7jHmN8NclxYTolv8JLWjxsl/MGnNkAgIo4HS6863vJyw/C12zfVtr7e+XaaCXdi
B7ycTMWB/GmstQd9tiVR6O6wWch6IpohOmaKjHgcA43+rjqtyHAHe4C1oir8A4F8
0aCqv+D4ANhSqLM3cqxrghcoUnSLzy8CiluMMUn+l6booC/CvF585diKFqnyAkxI
zqnHR6kWuRwY4AuEz1MmCUyebx1da8Vd/iJ6ErelqL8/kMaIUD/mMcCAUv7lGYDF
IiNt/U143QDSw5mBw1O06aSsY2He1AAI9g6nZwIDAQABAoIBACz95cekYaHggFZH
5RXU84br+ccVrOmKsiq+VUcG+VAc3SYGfITSLhmj23H0oepBSzsavMRPyAXo1viB
Bz0CaV6DRW9NkNPcAgA/2yhuZ+4s7pZHk45O0aLzuFHctxGteIV+b7FhadkyN2Ro
/CgfSAZUY2vhqo41p0jPBsCsx0Keq3pJIGg9FIHMDHUinBxa0RNhAuiamu9isVVz
032IU9Wx7utMA3h2i4pZuaKTJ/FsDPQ9aSY5dIfp0hIPWaHDstTKEoLF2/BWCd93
FjVR8Z9BbzoGs6UYaaqMfO93Yoxz0fIik9qkmke3iHaeRqJk+R/JoHr4LhOsD0qb
bBuULvECgYEA4/JJfaQyjTonjoS6q61LAlKNdfI9XRLkzPchtOT524Q4OSDnBDpg
5Afy15wITHtnNFOvt3bJrMDjwDn3am8VL18SRVAwDiBJ4NzTrpBZfYh7CJOqMCwC
CPO/Vm+FttmvCuuaAblrYOszhd5lC7N69QaCRJiDxdOAjBeHiC7NT7MCgYEA4DSi
wKcumKvhcg+qZ5kU2TDc0E3Jt6mtVjkPDgwP5Fxoht9aGlP0ldLedLe41Th3SU6e
RuOz9lAHaM1A1amdwTP9gF/yd92lTzDP9kbalHSNjDW84OB8RwOnSoilT9ZzNBnJ
ZwGMZFnuITNAafnn7SCa8ODoK7iTCIHXDm+vz30CgYEAmKtQGXx99yT6FXREanN4
h6eu405JVysuXzEuPDAYQLQ/y9ODpstK1a+VMF9rF36XUu6yA9jlnnTalYa9dWXM
9Jtia1YXuX5avOZqSMKZjYB5lvb/x5/SBRjsEAJFtn/5wwCld34usw0UxxZ66ulc
8vtXCIZ1y2uq7ylbNxTRog0CgYEAiaqoOKUu7l2zy2alGoGblJT1MQ5iityr62KT
xOtRIsY/BHnGiJ3+c7SMFZzt6DaIwEF+3EZarSaMtiQ56DgC/qvev2Gqr0EwjQSK
3Uy6UCeU9n/UnzwX8z7iDNkEsJYcHOSsjwwbWU8C8e3XYnsplqfLm5Zt2NK3raSU
GXAowr0CgYA4dwd199bs9oETfWIz+wd0UqyIy+MdHa0sZFYoY4dqNWruLVL3SfXO
899Jlrtg6OYtBe/ugjUueTffDXKsIlSBo6wgKTUlWkUejDwNQEnlAGtuuWyc7BAI
z7d7vzeVQ+gPg5K2DCHh6Y9TeZhRaDE4m/UYZOak5YUQu5zyzz7HBw==
""",
        )
        m.setattr(
            SETTINGS, "fernet_key", "DsitoKkQxZvA1C6LWR_uU_LnyH83S2CNv-w6qxqks50="
        )
        yield m


# This is the default scope, but it must not be changed
@pytest.fixture(autouse=True, scope="function")
def mock_get_session(monkeypatch):
    """Overrides database connections with an in-memory SQLite database"""
    with monkeypatch.context() as m:
        # Using the engine configuration from: https://docs.sqlalchemy.org/en/21/dialects/sqlite.html#using-staticpool-for-single-connection-memory-databases
        # Pytest runs fixtures and tests on separate threads, and this configuration makes that behave appropriately
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)

        def get_session(*args, **kwargs) -> Session:
            return Session(engine)

        m.setattr(database, "get_session", get_session)

        yield get_session


TEST_USER_ID = 0


# Keep the scope in sync with mock_get_session
@pytest.fixture(autouse=True, scope="function")
def default_database(mock_get_session: Callable[[], Session]):
    with mock_get_session() as session:
        session.add(
            model.AuthUser(
                user_id=TEST_USER_ID,
                email="test@email.com",
                totp_enabled=False,
                permissions=auth_module.Permissions(
                    tier=auth_module.PermissionTier.adminstrator, children={}
                ).model_dump(mode="json"),
            )
        )
        session.commit()


@pytest.fixture(autouse=True)
def override_permissions(request: pytest.FixtureRequest, monkeypatch):
    with monkeypatch.context() as m:
        if "logged_out" not in request.keywords:

            def mock_user_id(request: Request) -> int | None:
                return TEST_USER_ID

            monkeypatch.setitem(
                app.dependency_overrides, auth_module.user_id, mock_user_id
            )
        yield m


@pytest.fixture()
def mock_provider(mock_get_session) -> uuid.UUID:
    id = uuid.uuid4()
    set_module_config(
        PaymentModuleConfig(
            payment_options={
                id: PaymentOption(
                    name="Example",
                    description="Example Provider",
                    provider=MockPaymentProvider(),
                )
            }
        )
    )
    return id


@pytest.fixture(autouse=True)
def mock_mail_provider(monkeypatch):
    provider = MockMailProvider()

    def mock_mail(mail: Email, _):
        provider.send_mail(mail)

    with monkeypatch.context() as m:
        m.setattr("mail.handle_provider.handle_send_email", mock_mail)
        yield provider


@pytest.fixture()
def mock_member_type(mock_get_session) -> uuid.UUID:
    with mock_get_session() as session:
        member_type = model.MemberType(name="ExampleType", price=10_000)
        session.add(member_type)
        session.commit()
        session.refresh(member_type)
        return member_type.id
