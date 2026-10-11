from sqlalchemy import select
from sqlalchemy.orm import Session

import smtplib

from database.mail_providers import GmailAppPasswordMailProvider
from database.types import MailProviderType
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


def handle_send_email(mail: Email, provider: model.MailSender):
    match provider.provider:
        case MailProviderType.GMAIL_APP_PASSWORD:
            assert isinstance(provider, GmailAppPasswordMailProvider)
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
                smtp_server.login(provider.google_username, provider.app_password)
                smtp_server.send_message(
                    mail.into_py_email(sender=provider.google_username)
                )
