# Define global fixtures


import database
from database.base import Base
from main import app
from settings import SETTINGS

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
        monkeypatch.setattr(SETTINGS, "testing", True)
        yield m


@pytest.fixture(autouse=True)
def mock_get_session(monkeypatch):
    with monkeypatch.context() as m:
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
