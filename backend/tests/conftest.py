# Define global fixtures

import pytest
from main import app
from fastapi.testclient import TestClient


@pytest.fixture
def test_server() -> TestClient:
    """Returns a TestClient around the app from main.py"""
    return TestClient(app)
