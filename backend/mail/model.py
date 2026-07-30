from datetime import datetime
from email.message import EmailMessage
from typing import Literal, Optional

from pydantic import Field

from utils import BaseModel


class Email(BaseModel):
    """All metadata and content for an email"""

    sender: str
    recipients: list[str]
    subject: str
    content: str

    def redact(self) -> RedactedEmail:
        """Create a :class:`~RedactedEmail` by redacting the content of this email"""
        return RedactedEmail(
            sender=self.sender,
            recipients=self.recipients,
            subject=self.subject,
            content="[Redacted]",
        )

    def into_py_email(self) -> EmailMessage:
        """Converts to the python standard library email type, :class:`~EmailMessage`."""
        message = EmailMessage()
        message.set_content(self.content)
        message["To"] = ", ".join(self.recipients)
        message["From"] = self.sender
        message["Subject"] = self.subject
        return message


class RedactedEmail(BaseModel):
    """The metadata of an Email, without the content. (See also the :class:`~Email` class)"""

    sender: str
    recipients: list[str]
    subject: str
    # It's a waste to serialize or deserialize a non-discriminant literalfield
    # It only exists as a convenience for `t: Email | RedactedEmail` to have `t.content` be accessible.
    content: Literal["[Redacted]"] = Field(exclude=True)

    # Method defined so that if `t: Email | RedactedEmail`, then `t.redact()` is valid
    def redact(self) -> RedactedEmail:
        return self


class FailedEmail[T: Email | RedactedEmail](BaseModel):
    """An email that failed to send."""

    id: int
    last_sent: datetime
    retries: int
    email: T
    error: Optional[str]

    def redact(self) -> FailedEmail[RedactedEmail]:
        """Returns an identical FailedEmail, except the email content has been redacted"""
        return FailedEmail(
            id=self.id,
            last_sent=self.last_sent,
            retries=self.retries,
            email=self.email.redact(),
            error=self.error,
        )
