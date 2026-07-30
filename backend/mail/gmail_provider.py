from email.message import EmailMessage
from typing import Literal

from pydantic import Field

from .module import MailProviderInterface


class GmailProvider(MailProviderInterface):
    service_name: Literal["gmail"] = Field(default="gmail")

    def send_mail(self, mail: EmailMessage):
        raise NotImplementedError("TODO")
