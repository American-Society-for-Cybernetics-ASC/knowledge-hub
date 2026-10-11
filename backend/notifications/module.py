from sqlalchemy import false, select

import database
from database import model
from mail import mail_module
from mail.model import Email
from utils import BaseModel


class NotificationData(BaseModel):
    user_id: int
    subject: str
    message: str


class NotificationsModule:
    # Haven't set default=None for email_provider: not sending an email is explicit
    def create_notification(
        self, notification: NotificationData, email_provider: model.MailSender | None
    ):
        """
        Create a notification, sending an email if a provider is provided
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

        if email_provider:
            user = session.get(model.AuthUser, notification.user_id)
            if user:
                mail = Email(
                    recipients=[user.email],
                    subject=f"CKH Notification: {notification.subject}",
                    content=notification.message,
                )
                with session.begin_nested():
                    mail_module.send_mail(session, mail, email_provider)

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
