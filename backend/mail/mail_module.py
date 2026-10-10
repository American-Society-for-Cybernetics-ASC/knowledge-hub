from sqlalchemy import select
from sqlalchemy.orm import Session

from mail.handle_provider import handle_send_email
from mail.model import Email, FailedEmail
from database import model


def get_failed_emails(session: Session) -> list[FailedEmail[Email]]:
    """Get all emails that have failed to send"""
    return list(
        map(
            FailedEmail[Email].model_validate_sqlalchemy,
            session.execute(select(model.FailedEmailTable)).scalars().all(),
        )
    )


def send_mail(session: Session, mail: Email, provider: model.MailSender):
    """Attempt to send an email. Adds it to :class:`~database.model.FailedEmailTable` on failure"""
    error = None
    try:
        handle_send_email(mail, provider)
    except Exception as e:
        error = str(e)

    # Failed to send: add it to the failed email table.
    if error:
        with session.begin_nested():
            session.add(
                model.FailedEmailTable(email=mail.model_dump(mode="json"), error=error)
            )
