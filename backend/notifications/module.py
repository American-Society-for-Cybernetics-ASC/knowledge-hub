from sqlalchemy import select

import database
from database import model
from mail.module import MailModule
from mail.model import Email
from settings import SETTINGS
from utils import BaseModel


class NotificationData(BaseModel):
    user_id: int
    message: str
    notification_type: str
    send_email: bool = False
    email_subject: str = ""
    email_content: str = ""


class NotificationsModule:

    def _get_sender(self) -> str:
        return SETTINGS.google_username or "noreply@ckh.asc-cybernetics.org"

    def create_notification(self, notification: NotificationData):
        """
       To create a notification and send an email if the conditions are met
        """
        session = database.get_session()

        new_notification = model.Notification(
            user_id=notification.user_id,
            message=notification.message,
            notification_type=notification.notification_type,
            status="unread",
            send_email=notification.send_email,
        )
        session.add(new_notification)
        session.commit()

        if notification.send_email and notification.email_subject and notification.email_content:
            user = session.get(model.AuthUser, notification.user_id)
            if user and user.email:
                mail = Email(
                    sender=self._get_sender(),
                    recipients=[user.email],
                    subject=notification.email_subject,
                    content=notification.email_content,
                )
                MailModule().send_mail(mail)

    def get_notifications(
        self,
        user_id: int,
        status: str | None = None,
    ) -> list[model.Notification]:
        """
        To return a list of notification to a user. 
        """
        session = database.get_session()

        query = select(model.Notification).where(
            model.Notification.user_id == user_id
        )

        if status:
            query = query.where(model.Notification.status == status)

        query = query.order_by(model.Notification.created_at.desc())

        return list(session.execute(query).scalars().all())

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        Modify the status of the notification for a particular user
        """
        session = database.get_session()

        notification = session.get(model.Notification, notification_id)

        if not notification or notification.user_id != user_id:
            return False

        notification.status = "read"
        session.commit()

        return True