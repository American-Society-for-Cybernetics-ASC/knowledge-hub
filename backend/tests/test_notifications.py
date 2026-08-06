from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Callable

from database import model


def test_create_and_get_notification(test_server: TestClient, mock_get_session: Callable[[], Session]):
    """Test creating a notification and retrieving it"""
    session = mock_get_session()

    # Create a user first
    user = model.AuthUser(
        email="test@example.com",
        hash_password="hashed",
        totp_enabled=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create a notification directly via module
    notification = model.Notification(
        user_id=user.user_id,
        message="Your application has been approved.",
        notification_type="application_approved",
        status="unread",
        send_email=False,
    )
    session.add(notification)
    session.commit()

    # Get notifications
    response = test_server.get(f"/notifications/?user_id={user.user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["message"] == "Your application has been approved."
    assert data[0]["status"] == "unread"


def test_filter_notifications_by_status(test_server: TestClient, mock_get_session: Callable[[], Session]):
    """Test filtering notifications by unread status"""
    session = mock_get_session()

    user = model.AuthUser(
        email="test@example.com",
        hash_password="hashed",
        totp_enabled=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Add one unread and one read notification
    session.add(model.Notification(
        user_id=user.user_id,
        message="Unread notification",
        notification_type="test",
        status="unread",
        send_email=False,
    ))
    session.add(model.Notification(
        user_id=user.user_id,
        message="Read notification",
        notification_type="test",
        status="read",
        send_email=False,
    ))
    session.commit()

    # Filter by unread
    response = test_server.get(f"/notifications/?user_id={user.user_id}&status=unread")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["message"] == "Unread notification"


def test_mark_notification_as_read(test_server: TestClient, mock_get_session: Callable[[], Session]):
    """Test marking a notification as read"""
    session = mock_get_session()

    user = model.AuthUser(
        email="test@example.com",
        hash_password="hashed",
        totp_enabled=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    notification = model.Notification(
        user_id=user.user_id,
        message="Test notification",
        notification_type="test",
        status="unread",
        send_email=False,
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)

    # Mark as read
    response = test_server.patch(
        f"/notifications/{notification.notification_id}/read?user_id={user.user_id}"
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Notification marked as read."

    # Verify it is now read
    response = test_server.get(f"/notifications/?user_id={user.user_id}&status=unread")
    assert response.json() == []


def test_mark_notification_wrong_user(test_server: TestClient, mock_get_session: Callable[[], Session]):
    """Test that a user cannot mark another user's notification as read"""
    session = mock_get_session()

    user1 = model.AuthUser(
        email="user1@example.com",
        hash_password="hashed",
        totp_enabled=False,
    )
    user2 = model.AuthUser(
        email="user2@example.com",
        hash_password="hashed",
        totp_enabled=False,
    )
    session.add_all([user1, user2])
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    notification = model.Notification(
        user_id=user1.user_id,
        message="User1 notification",
        notification_type="test",
        status="unread",
        send_email=False,
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)

    # User2 tries to mark user1's notification as read
    response = test_server.patch(
        f"/notifications/{notification.notification_id}/read?user_id={user2.user_id}"
    )
    assert response.status_code == 404