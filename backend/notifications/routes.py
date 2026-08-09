from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from utils import BaseModel
from . import NotificationsModule


notifications_router = APIRouter(prefix="/notifications")


class NotificationResponse(BaseModel):
    notification_id: int
    user_id: int
    subject: str
    message: str
    read: bool


@notifications_router.get("/")
def get_notifications(
    module: Annotated[NotificationsModule, Depends(NotificationsModule)],
    user_id: int,
    unread_only: bool = False,
) -> list[NotificationResponse]:
    """
    Returns notifications for a user
    """
    # TODO: validate User permissions
    notifications = module.get_notifications(user_id=user_id, unread_only=unread_only)
    return [NotificationResponse.model_validate_sqlalchemy(n) for n in notifications]


@notifications_router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    module: Annotated[NotificationsModule, Depends(NotificationsModule)],
) -> dict:
    """
    Marks a notification as read
    """
    success = module.mark_as_read(notification_id=notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"message": "Notification marked as read."}
