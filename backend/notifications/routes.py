from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import model
from . import NotificationsModule


notifications_router = APIRouter(prefix="/notifications")


class NotificationResponse(BaseModel):
    notification_id: int
    user_id: int
    message: str
    notification_type: str
    status: str

    model_config = {"from_attributes": True}


@notifications_router.get("/")
def get_notifications(
    user_id: int,
    status: Optional[str] = None,
    module: Annotated[NotificationsModule, Depends(NotificationsModule)] = None,
) -> list[NotificationResponse]:
    """
    Returns notifications for a user
    """
    notifications = module.get_notifications(user_id=user_id, status=status)
    return [NotificationResponse.model_validate(n) for n in notifications]


@notifications_router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    user_id: int,
    module: Annotated[NotificationsModule, Depends(NotificationsModule)] = None,
) -> dict:
    """
    Marks a notification as read
    """
    success = module.mark_as_read(
        notification_id=notification_id,
        user_id=user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"message": "Notification marked as read."}