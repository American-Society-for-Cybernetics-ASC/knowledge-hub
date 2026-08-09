from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Callable

from database import model
from notifications.module import NotificationsModule, NotificationData


def test_create_and_get_notification(
    test_server: TestClient, mock_get_session: Callable[[], Session]
):
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
    NotificationsModule().create_notification(
        NotificationData(
            user_id=user.user_id,
            subject="Application Approved",
            message="Your application has been approved.",
            send_email=False,
        )
    )

    # Get notifications
    response = test_server.get(f"/notifications/?user_id={user.user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["subject"] == "Application Approved"
    assert data[0]["message"] == "Your application has been approved."
    assert not data[0]["read"]


def test_filter_unread_notifications(
    test_server: TestClient, mock_get_session: Callable[[], Session]
):
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
    session.add(
        model.Notification(
            user_id=user.user_id,
            subject="Unread",
            message="Unread notification",
            read=False,
        )
    )
    session.add(
        model.Notification(
            user_id=user.user_id,
            subject="Read",
            message="Read notification",
            read=True,
        )
    )
    session.commit()

    # Filter by unread
    response = test_server.get(
        f"/notifications/?user_id={user.user_id}&unread_only=true"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["subject"] == "Unread"


def test_mark_notification_as_read(
    test_server: TestClient, mock_get_session: Callable[[], Session]
):
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
        subject="Test",
        message="Test notification",
        read=False,
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)

    # Mark as read
    response = test_server.patch(f"/notifications/{notification.notification_id}/read")
    assert response.status_code == 200
    assert response.json()["message"] == "Notification marked as read."

    # Verify it is now read
    response = test_server.get(
        f"/notifications/?user_id={user.user_id}&unread_only=true"
    )
    assert response.json() == []


def test_mark_nonexistent_notification(test_server: TestClient):
    """Test that marking a nonexistent notification returns 404"""
    response = test_server.patch("/notifications/99999/read")
    assert response.status_code == 404
