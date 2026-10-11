import uuid

from database.model import MailSender
from database.types import MailProviderType

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class GmailAppPasswordMailProvider(MailSender):
    _IDENTITY = MailProviderType.GMAIL_APP_PASSWORD
    __tablename__ = "mail_provider_" + _IDENTITY

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey(MailSender.id), primary_key=True)
    google_username: Mapped[str]
    app_password: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": _IDENTITY,
    }
