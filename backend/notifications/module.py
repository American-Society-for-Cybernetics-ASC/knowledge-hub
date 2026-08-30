from sqlalchemy import false, select

import database
from database import model
from mail.module import MailModule
from mail.model import Email
from settings import SETTINGS
from utils import BaseModel


class NotificationData(BaseModel):
    user_id: int
    subject: str
    message: str
    send_email: bool = False


class NotificationsModule:
    def _get_sender(self) -> str:
        return SETTINGS.google_username or "noreply@ckh.asc-cybernetics.org"

    def create_notification(self, notification: NotificationData):
        """
        To create a notification and send an email if the conditions are met
        """
        with database.get_session() as session:
            new_notification = model.Notification(
                user_id=notification.user_id,
                subject=notification.subject,
                message=notification.message,
                read=False,
            )
            session.add(new_notification)
            session.commit()

        if notification.send_email:
            user = session.get(model.AuthUser, notification.user_id)
            if user and user.email:
                mail = Email(
                    sender=self._get_sender(),
                    recipients=[user.email],
                    subject=f"CKH Notification: {notification.subject}",
                    content=notification.message,
                )
                MailModule().send_mail(mail)

    def get_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
    ) -> list[model.Notification]:
        """
        To return a list of notification to a user.
        """
        with database.get_session() as session:
            query = select(model.Notification).where(
                model.Notification.user_id == user_id
            )

            if unread_only:
                query = query.where(model.Notification.read == false())

            query = query.order_by(model.Notification.created_at.desc())

            return list(session.execute(query).scalars().all())

    def mark_as_read(self, notification_id: int) -> bool:
        """
        Modify the status of the notification for a particular user
        """
        with database.get_session() as session:
            notification = session.get(model.Notification, notification_id)

        if not notification:
            return False

        notification.read = True
        session.commit()

        return True
