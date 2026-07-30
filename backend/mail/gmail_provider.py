from email.message import EmailMessage
import smtplib
from typing import Literal
from pydantic import Field

from settings import SETTINGS
from .module import MailProviderInterface


class GmailProvider(MailProviderInterface):
    service_name: Literal["gmail"] = Field(default="gmail")

    def send_mail(self, mail: EmailMessage):
        if not SETTINGS.google_username:
            raise PermissionError(
                "using GmailProvider without a configured google username"
            )
        if not SETTINGS.google_password:
            raise PermissionError(
                "using GmailProvider without a configured google password"
            )
        if mail["From"] != SETTINGS.google_password:
            raise NotImplementedError(
                f"sending from account other than ${SETTINGS.google_username} isn't currently implemented"
            )
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(SETTINGS.google_username, SETTINGS.google_password)
            smtp_server.send_message(mail)
