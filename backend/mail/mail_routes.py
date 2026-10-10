from typing import Literal
import uuid

from fastapi import APIRouter, Depends, HTTPException

from auth_module import authorized
from auth_module.model import PermissionTier
from database.mail_providers import GmailAppPasswordMailProvider
from database.model import MailSender
from utils import BaseModel
import database
from database.types import MailProviderType, PermissionCategory
from .model import FailedEmail, RedactedEmail
from . import mail_module


mail_router = APIRouter(prefix="/mail", tags=["mail"])


@mail_router.get("/failed")
def get_failed_emails(
    _=Depends(authorized([PermissionCategory.MAIL], PermissionTier.manager)),
) -> list[FailedEmail[RedactedEmail]]:
    """Get all failed emails"""
    with database.with_transaction() as session:
        return list(map(FailedEmail.redact, mail_module.get_failed_emails(session)))


class ReadGmailAppPasswordMailProvider(BaseModel):
    provider_type: Literal[MailProviderType.GMAIL_APP_PASSWORD] = (
        MailProviderType.GMAIL_APP_PASSWORD
    )
    google_username: str
    app_password: str

    @staticmethod
    def from_db_model(
        option: GmailAppPasswordMailProvider,
    ) -> ReadGmailAppPasswordMailProvider:
        return ReadGmailAppPasswordMailProvider(
            google_username=option.google_username,
            app_password=option.app_password,
        )


type ReadMailProvider = ReadGmailAppPasswordMailProvider


class ReadMailSender(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    provider: ReadMailProvider

    @staticmethod
    def from_db_model(option: MailSender) -> ReadMailSender:
        provider: ReadMailProvider
        match option.provider:
            case MailProviderType.GMAIL_APP_PASSWORD:
                assert isinstance(option, GmailAppPasswordMailProvider)
                provider = ReadGmailAppPasswordMailProvider.from_db_model(option)
        return ReadMailSender(
            id=option.id,
            name=option.name,
            description=option.description,
            provider=provider,
        )


@mail_router.get("/senders")
def get_mail_senders(
    _=Depends(authorized([PermissionCategory.MAIL], PermissionTier.manager)),
) -> list[ReadMailSender]:
    with database.get_session() as session:
        return list(map(ReadMailSender.from_db_model, session.query(MailSender)))


class PostGmailAppPasswordMailProvider(BaseModel):
    provider_type: Literal[MailProviderType.GMAIL_APP_PASSWORD] = (
        MailProviderType.GMAIL_APP_PASSWORD
    )
    google_username: str
    app_password: str

    def to_db_model(self) -> GmailAppPasswordMailProvider:
        return GmailAppPasswordMailProvider(
            google_username=self.google_username, app_password=self.app_password
        )


type PostMailProvider = PostGmailAppPasswordMailProvider


class PostMailSender(BaseModel):
    name: str
    description: str
    provider: PostMailProvider

    def to_db_model(self) -> MailSender:
        record = self.provider.to_db_model()
        record.name = self.name
        record.description = self.description
        return record


@mail_router.post("/senders")
def post_mail_sender(
    provider: PostMailSender,
    _=Depends(authorized([PermissionCategory.MAIL], PermissionTier.manager)),
) -> ReadMailSender:
    with database.with_transaction() as session:
        record = provider.to_db_model()
        session.add(record)
    return ReadMailSender.from_db_model(record)


class PatchGmailAppPasswordMailProvider(BaseModel):
    provider_type: Literal[MailProviderType.GMAIL_APP_PASSWORD] = (
        MailProviderType.GMAIL_APP_PASSWORD
    )
    google_username: str | None = None
    app_password: str | None = None

    def patch_db_model(self, option: GmailAppPasswordMailProvider):
        option.google_username = self.google_username or option.google_username
        option.app_password = self.app_password or option.app_password


type PatchMailProvider = PatchGmailAppPasswordMailProvider


class PatchMailSender(BaseModel):
    name: str | None = None
    description: str | None = None
    provider: PatchMailProvider | None = None


@mail_router.patch("/senders/{sender_id}")
def patch_mail_sender(
    sender_id: uuid.UUID,
    patch: PatchMailSender,
    _=Depends(authorized([PermissionCategory.MAIL], PermissionTier.manager)),
) -> ReadMailSender:
    with database.with_transaction() as session:
        record = session.get(MailSender, sender_id)

        if record is None:
            raise HTTPException(404, "Not found")

        record.name = patch.name or record.name
        record.description = patch.description or record.description
        if patch.provider is not None:
            if patch.provider.provider_type != record.provider:
                raise HTTPException(400, "Can't change mail sender type after creation")
            patch.provider.patch_db_model(
                # Safety: above line ensures the types match.
                record  # type: ignore
            )

        return ReadMailSender.from_db_model(record)
