from datetime import datetime
from email.message import EmailMessage
from typing import Literal, Optional

from pydantic import Field

from utils import BaseModel


class RedactedEmail(BaseModel):
    sender: str
    recipients: list[str]
    subject: str
    content: Literal["[Redacted]"] = Field(exclude=True)

    def redact(self) -> RedactedEmail:
        return self


class Email(BaseModel):
    sender: str
    recipients: list[str]
    subject: str
    content: str

    def redact(self) -> RedactedEmail:
        return RedactedEmail(
            sender=self.sender,
            recipients=self.recipients,
            subject=self.subject,
            content="[Redacted]",
        )

    def into_py_email(self) -> EmailMessage:
        message = EmailMessage()
        message.set_content(self.content)
        message["To"] = ", ".join(self.recipients)
        message["From"] = self.sender
        message["Subject"] = self.subject
        return message


class FailedEmail[T: Email | RedactedEmail](BaseModel):
    id: int
    last_sent: datetime
    retries: int
    email: T
    error: Optional[str]

    def redact(self) -> FailedEmail[RedactedEmail]:
        return FailedEmail(
            id=self.id,
            last_sent=self.last_sent,
            retries=self.retries,
            email=self.email.redact(),
            error=self.error,
        )
