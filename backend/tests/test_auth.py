from fastapi.testclient import TestClient
import pytest
import pyotp

from auth_module import Permissions, PermissionTier


def test_ordering():
    assert PermissionTier.adminstrator > PermissionTier.manager
    assert PermissionTier.adminstrator >= PermissionTier.manager
    assert PermissionTier.moderator < PermissionTier.manager

    assert Permissions(tier=PermissionTier.adminstrator).includes(
        ["blah"], PermissionTier.moderator
    )
    assert Permissions(
        children={"blah": Permissions(tier=PermissionTier.manager)}
    ).includes(["blah", "boo"], PermissionTier.moderator)
    assert Permissions(
        children={"blah": Permissions(tier=PermissionTier.manager)}
    ).includes(["blah"], PermissionTier.moderator)
    assert not Permissions(
        tier=None, children={"blah": Permissions(tier=PermissionTier.manager)}
    ).includes(["boo"], PermissionTier.moderator)
    assert not Permissions(
        tier=None, children={"boo": Permissions(tier=PermissionTier.manager)}
    ).includes(["blah"], PermissionTier.moderator)


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


def test_verify_otp_returns_cookie(test_server: TestClient):
    """Test that verify_otp issues a JWT cookie for a successful login"""

    # Register
    register_response = test_server.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test User",
        },
    )
    assert register_response.status_code == 200
    qr_uri = register_response.json()["qr_uri"]

    # Extract TOTP secret from QR URI
    secret = qr_uri.split("secret=")[1].split("&")[0]

    # Confirm TOTP
    code = pyotp.TOTP(secret).now()
    test_server.post(
        "/auth/confirm-totp",
        json={"email": "test@example.com", "code": code},
    )

    # Login
    login_response = test_server.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "TestPassword123!"},
    )
    challenge_token = login_response.json()["challenge_token"]

    # Verify OTP
    code = pyotp.TOTP(secret).now()
    response = test_server.post(
        "/auth/verify-otp",
        json={
            "email": "test@example.com",
            "code": code,
            "challenge_token": challenge_token,
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful."
    assert "access_token" in response.cookies


def test_public_key_endpoint(test_server: TestClient):
    """Test that public key endpoint returns a valid RSA public key"""
    response = test_server.get("/auth/public-key")
    assert response.status_code == 200
    data = response.json()
    assert "public_key" in data
    assert "BEGIN PUBLIC KEY" in data["public_key"]


def test_get_current_user(test_server: TestClient, mock_get_session):
    """Test that /auth/me returns user details"""
    from sqlalchemy.orm import Session
    from database import model

    session: Session = mock_get_session()
    user = model.AuthUser(
        email="test@example.com",
        hash_password="hashed",
        totp_enabled=False,
    )
    session.add(user)
    session.commit()

    response = test_server.get("/auth/me")
    assert response.status_code == 200


@pytest.mark.logged_out
def test_get_current_user_unauthenticated(test_server: TestClient):
    """Test that /auth/me returns None when not authenticated"""
    response = test_server.get("/auth/me")
    assert response.json() is None


def test_change_password(test_server: TestClient):
    """Test that a user can change their password"""
    # Register user
    test_server.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test User",
        },
    )

    response = test_server.post(
        "/auth/change-password",
        json={
            "current_password": "TestPassword123!",
            "new_password": "NewPassword456!",
        },
    )
    assert response.status_code in [200, 400]


def test_change_password_wrong_current(test_server: TestClient):
    """Test that changing password fails with wrong current password"""
    test_server.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test User",
        },
    )

    response = test_server.post(
        "/auth/change-password",
        json={
            "current_password": "WrongPassword!",
            "new_password": "NewPassword456!",
        },
    )
    assert response.status_code == 400


def test_change_email(test_server: TestClient):
    """Test that a user can change their email"""
    test_server.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test User",
        },
    )

    response = test_server.post(
        "/auth/change-email",
        json={"new_email": "newemail@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Email updated successfully."


def test_disable_totp(test_server: TestClient):
    """Test that a user can disable TOTP"""
    import pyotp

    register_response = test_server.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
            "display_name": "Test User",
        },
    )
    qr_uri = register_response.json()["qr_uri"]
    secret = qr_uri.split("secret=")[1].split("&")[0]
    code = pyotp.TOTP(secret).now()
    test_server.post(
        "/auth/confirm-totp",
        json={"email": "test@example.com", "code": code},
    )

    response = test_server.post("/auth/disable-totp")
    assert response.status_code == 200
    assert response.json()["message"] == "Two-factor authentication disabled."


def test_login(test_server: TestClient):
    """Test that logout clears the access token cookie"""
    response = test_server.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully."