import smtplib

from database.mail_providers import GmailAppPasswordMailProivder
from database.types import MailProviderType
from mail.model import Email
import database
import database.model


def handle_send_email(mail: Email, provider: database.model.MailProvider):
    match provider.provider:
        case MailProviderType.GMAIL_APP_PASSWORD:
            assert isinstance(provider, GmailAppPasswordMailProivder)
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
                smtp_server.login(provider.google_username, provider.app_password)
                smtp_server.send_message(
                    mail.into_py_email(sender=provider.google_username)
                )
