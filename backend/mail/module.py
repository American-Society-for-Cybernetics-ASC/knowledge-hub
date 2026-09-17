from sqlalchemy import select

from utils.module_config import ModuleConfig, get_module_config
from mail.model import Email, FailedEmail
import database
from database import model

from typing import Annotated, Optional, Union
from pydantic import Field

from .provider.gmail_provider import GmailProvider
from .provider.mock_provider import MockMailProvider


class MailModule:
    def get_failed_emails(self) -> list[FailedEmail[Email]]:
        """Get all emails that have failed to send"""
        with database.get_session() as session:
            return list(
                map(
                    FailedEmail[Email].model_validate_sqlalchemy,
                    session.execute(select(model.FailedEmailTable)).scalars().all(),
                )
            )

    def send_mail(self, mail: Email):
        """Attempt to send an email. Adds it to :class:`~database.model.FailedEmailTable` on failure"""
        config = get_module_config(MailModuleConfig)
        if config.provider:
            try:
                config.provider.send_mail(mail)
                return
            except Exception as e:
                error = str(e)
        else:
            error = "No email provider configured"

        # Failed to send: add it to the failed email table.
        with database.get_session() as session:
            session.add(model.FailedEmailTable(email=mail.model_dump(), error=error))
            session.commit()


type MailProvider = Annotated[
    Union[MockMailProvider, GmailProvider], Field(discriminator="service_name")
]
"""
Update this Union to add new MailProvider types. Make sure all members implement MailProviderInterface

Make sure your subclass has class variable `service_name: Literal[discriminant]`
where discriminant is a unique string literal (see MockMailProvider ).
"""


class MailModuleConfig(ModuleConfig):
    provider: Optional[MailProvider]

    @staticmethod
    def module_id():
        return "mail"

    @classmethod
    def default(cls) -> MailModuleConfig:
        return MailModuleConfig(provider=None)
