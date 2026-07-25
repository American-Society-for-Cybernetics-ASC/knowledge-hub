# Define global fixtures

import pytest
from main import app
from fastapi.testclient import TestClient
from settings import settings


@pytest.fixture
def test_server() -> TestClient:
    """Returns a TestClient around the app from main.py"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    """Override settings as needed for tests"""
    monkeypatch.setattr(settings, "testing", True)
