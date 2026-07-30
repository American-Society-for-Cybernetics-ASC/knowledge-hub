from .gmail_provider import GmailProvider
import database
from database import model

from abc import abstractmethod
from email.message import EmailMessage
from typing import Annotated, Literal, LiteralString, Optional, Union
from pydantic import BaseModel, Field
from sqlalchemy.exc import NoResultFound


class MailModule:
    MODULE_ID = "mail"

    def get_config(self) -> MailModuleConfig:
        """Fetch the module's config from the database"""
        session = database.get_session()
        try:
            config_record = session.get_one(model.Module, MailModule.MODULE_ID)
            return MailModuleConfig.model_validate(config_record.config)
        except NoResultFound:
            config_record = model.Module(
                module_name=MailModule.MODULE_ID,
                config=MailModuleConfig.default().model_dump_json(),
            )
            session.add(config_record)
            session.commit()
            return self.get_config()

    def send_mail(self, mail: EmailMessage):
        config = self.get_config()
        if config.provider:
            config.provider.send_mail(mail)

        # TODO: dead letter queue


class MailModuleConfig(BaseModel):
    provider: Optional[MailProvider]

    @staticmethod
    def default() -> MailModuleConfig:
        return MailModuleConfig(provider=None)


type MailProvider = Annotated[
    Union[TestMailProvider, GmailProvider], Field(discriminator="service_name")
]


class MailProviderInterface(BaseModel):
    @property
    @abstractmethod
    def service_name(self) -> LiteralString:
        pass

    @abstractmethod
    def send_mail(self, mail: EmailMessage): ...


_sent_mail: list[EmailMessage] = []


class TestMailProvider(MailProviderInterface):
    service_name: Literal["test"] = Field(default="test")

    def send_mail(self, mail: EmailMessage):
        _sent_mail.append(mail)

    @staticmethod
    def sent_mail() -> list[EmailMessage]:
        return _sent_mail
