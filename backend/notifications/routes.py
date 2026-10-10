from typing import Annotated, Literal
import uuid
from fastapi import APIRouter, Depends, HTTPException

from auth_module import authorized
from auth_module.model import PermissionTier
from database.types import PermissionCategory
from utils.module_config import get_module_config
import database
from database.module_configs import NotificationsConfig
from utils import BaseModel
from . import NotificationsModule


notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])


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


class ReadNotificationConfig(BaseModel):
    email_provider: uuid.UUID | Literal[""]

    @staticmethod
    def from_db_model(config: NotificationsConfig) -> ReadNotificationConfig:
        return ReadNotificationConfig(
            email_provider=""
            if config.email_provider is None
            else config.email_provider
        )


@notifications_router.get("/config")
def get_notification_config(
    _=Depends(authorized([PermissionCategory.NOTIFICATIONS], PermissionTier.manager)),
):
    with database.get_session() as session:
        config = get_module_config(session, NotificationsConfig)
        return ReadNotificationConfig.from_db_model(config)


class PatchNotificationConfig(BaseModel):
    email_provider: uuid.UUID | Literal[""] | None = None


@notifications_router.patch("/config")
def patch_notification_config(
    patch: PatchNotificationConfig,
) -> ReadNotificationConfig:
    with database.with_transaction() as session:
        config = get_module_config(session, NotificationsConfig)

        if patch.email_provider == "":
            config.email_provider = None
        elif patch.email_provider is not None:
            config.email_provider = patch.email_provider

        return ReadNotificationConfig.from_db_model(config)
