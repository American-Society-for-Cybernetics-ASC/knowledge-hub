# Define global fixtures


from typing import Callable

from mail.module import MailModule, MailModuleConfig
from mail.provider.mock_provider import MockMailProvider

import database
from database import model
from database.base import Base

from settings import SETTINGS

from pytest import MonkeyPatch

# Stops us from running startup scripts
with MonkeyPatch().context() as m:
    m.setattr(SETTINGS, "testing", True)
    from main import app

import pytest
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


# Keep the scope in sync with mock_get_session
@pytest.fixture(scope="function")
def default_database(mock_get_session: Callable[[], Session]):
    session = mock_get_session()
    session.add(
        model.Module(
            module_name=MailModule.MODULE_ID,
            config=MailModuleConfig(provider=MockMailProvider()).model_dump(),
        )
    )
    session.commit()
