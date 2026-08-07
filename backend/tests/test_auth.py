from fastapi.testclient import TestClient

from auth_module import Permission, PermissionTier


def test_ordering():
    assert PermissionTier.adminstrator > PermissionTier.manager
    assert PermissionTier.adminstrator >= PermissionTier.manager
    assert PermissionTier.moderator < PermissionTier.manager

    assert Permission(heirarchy=[], tier=PermissionTier.adminstrator).includes(
        Permission(heirarchy=["blah"], tier=PermissionTier.moderator)
    )
    assert Permission(heirarchy=["blah"], tier=PermissionTier.manager).includes(
        Permission(heirarchy=["blah", "blah"], tier=PermissionTier.moderator)
    )
    assert not Permission(heirarchy=["blah"], tier=PermissionTier.manager).includes(
        Permission(heirarchy=["boo"], tier=PermissionTier.manager)
    )
    assert not Permission(heirarchy=["boo"], tier=PermissionTier.manager).includes(
        Permission(heirarchy=["blah"], tier=PermissionTier.manager)
    )


def test_register_success(test_server: TestClient):
    """Test that a new user can register successfully"""
    response = test_server.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "qr_uri" in data
    assert "otpauth://" in data["qr_uri"]
    assert (
        data["message"]
        == "Registration successful. Please scan the QR code with your authenticator app."
    )


def test_register_duplicate_email(test_server: TestClient):
    """Test that registering with an existing email fails"""
    test_server.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test User",
        },
    )

    response = test_server.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "AnotherPassword123!",
            "display_name": "Another User",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_wrong_password(test_server: TestClient):
    """Test that login fails with wrong password"""
    test_server.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test User",
        },
    )

    response = test_server.post(
        "/auth/login", json={"email": "test@example.com", "password": "WrongPassword!"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(test_server: TestClient):
    """Test that login fails for a user that does not exist"""
    response = test_server.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "TestPassword123!"},
    )
    assert response.status_code == 401


def test_register_and_login_success(test_server: TestClient):
    """Test full registration and login flow"""
    register_response = test_server.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test User",
        },
    )
    assert register_response.status_code == 200

    login_response = test_server.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "TestPassword123!"},
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert "challenge_token" in data


def test_account_lockout_after_failed_attempts(test_server: TestClient):
    """Test that account locks temporarily after 3 failed attempts"""
    test_server.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test User",
        },
    )

    for _ in range(3):
        test_server.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "WrongPassword!"},
        )

    response = test_server.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "TestPassword123!"},
    )
    assert response.status_code == 401
    assert "locked" in response.json()["detail"].lower()
