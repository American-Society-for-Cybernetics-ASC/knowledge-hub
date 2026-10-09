import uuid

from database.model import MailProvider
from database.types import MailProviderType

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class GmailAppPasswordMailProivder(MailProvider):
    _IDENTITY = MailProviderType.GMAIL_APP_PASSWORD
    __tablename__ = "mail_provider_" + _IDENTITY

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey(MailProvider.id), primary_key=True)
    google_username: Mapped[str]
    app_password: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": _IDENTITY,
    }
