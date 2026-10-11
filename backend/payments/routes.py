from typing import Annotated, Literal
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, HTTPException

from auth_module import authorized, user_id
from auth_module.model import PermissionTier
from database.model import PaymentOption
from database.payment_providers import MockPaymentProvider, StripePaymentProvider
from database.types import PaymentProviderType, PermissionCategory
from database.products import DonationProduct
import database
from utils import BaseModel
from .payment import Payment, ReadPayment
from .transactions import Transaction, TransactionTypes
from .module import PaymentsModule
from .exceptions import (
    PaymentAlreadyComplete,
    PaymentNotYoursError,
    PaymentProviderError,
    PaymentNotFoundError,
    TransactionInProgressError,
    TransactionNotFoundError,
    TransactionNotSuccessful,
)


payments_router = APIRouter(prefix="/payments", tags=["payments", "admin"])


# --- /providers/admin ---
class ReadMockPaymentProvider(BaseModel):
    provider_type: Literal[PaymentProviderType.MOCK] = PaymentProviderType.MOCK

    @staticmethod
    def from_db_model(_option: MockPaymentProvider) -> ReadMockPaymentProvider:
        return ReadMockPaymentProvider()


class ReadStripePaymentProvider(BaseModel):
    provider_type: Literal[PaymentProviderType.STRIPE] = PaymentProviderType.STRIPE
    api_key: str
    publishable_key: str
    webhook_secret: str

    @staticmethod
    def from_db_model(option: StripePaymentProvider) -> ReadStripePaymentProvider:
        return ReadStripePaymentProvider(
            api_key=option.api_key,
            publishable_key=option.publishable_key,
            webhook_secret=option.webhook_secret,
        )


type ReadPaymentProvider = ReadMockPaymentProvider | ReadStripePaymentProvider


class AdminReadPaymentOption(BaseModel):
    id: UUID
    name: str
    description: str
    provider: ReadPaymentProvider

    @staticmethod
    def from_db_model(option: PaymentOption) -> AdminReadPaymentOption:
        provider: ReadPaymentProvider
        match option.provider:
            case PaymentProviderType.STRIPE:
                assert isinstance(option, StripePaymentProvider)
                provider = ReadStripePaymentProvider.from_db_model(option)
            case PaymentProviderType.MOCK:
                assert isinstance(option, MockPaymentProvider)
                provider = ReadMockPaymentProvider.from_db_model(option)
        return AdminReadPaymentOption(
            id=option.id,
            name=option.name,
            description=option.description,
            provider=provider,
        )


@payments_router.get("/providers/admin")
def get_config(
    _=Depends(authorized([PermissionCategory.PAYMENT], PermissionTier.manager)),
) -> list[AdminReadPaymentOption]:
    with database.get_session() as session:
        return list(
            map(AdminReadPaymentOption.from_db_model, session.query(PaymentOption))
        )


class PatchMockPaymentProvider(BaseModel):
    provider_type: Literal[PaymentProviderType.MOCK] = PaymentProviderType.MOCK

    def patch_db_model(self, option: MockPaymentProvider):
        pass


class PatchStripePaymentProvider(BaseModel):
    provider_type: Literal[PaymentProviderType.STRIPE] = PaymentProviderType.STRIPE
    api_key: str | None = None
    publishable_key: str | None = None
    webhook_secret: str | None = None

    def patch_db_model(self, option: StripePaymentProvider):
        option.api_key = self.api_key or option.api_key
        option.publishable_key = self.publishable_key or option.publishable_key
        option.webhook_secret = self.webhook_secret or option.webhook_secret


type PatchPaymentProvider = PatchMockPaymentProvider | PatchStripePaymentProvider


class PatchPaymentOption(BaseModel):
    name: str | None = None
    description: str | None = None
    provider: PatchPaymentProvider | None = None


@payments_router.patch("/providers/{provider_id}")
def patch_provider(
    provider_id: uuid.UUID,
    patch: PatchPaymentOption,
    _=Depends(authorized([PermissionCategory.PAYMENT], PermissionTier.manager)),
) -> AdminReadPaymentOption:
    with database.with_transaction() as session:
        record = session.get(PaymentOption, provider_id)

        if record is None:
            raise HTTPException(404, "Not found")

        record.name = patch.name or record.name
        record.description = patch.description or record.description
        if patch.provider is not None:
            if patch.provider.provider_type != record.provider:
                raise HTTPException(400, "Can't change option type after creation")
            patch.provider.patch_db_model(
                # Safety: above line ensures the types match.
                record  # type: ignore
            )

        return AdminReadPaymentOption.from_db_model(record)


class PostMockPaymentProvider(BaseModel):
    provider_type: Literal[PaymentProviderType.MOCK] = PaymentProviderType.MOCK

    def to_db_model(self) -> MockPaymentProvider:
        return MockPaymentProvider()


class PostStripePaymentProvider(BaseModel):
    provider_type: Literal[PaymentProviderType.STRIPE] = PaymentProviderType.STRIPE
    api_key: str
    publishable_key: str
    webhook_secret: str

    def to_db_model(self) -> StripePaymentProvider:
        return StripePaymentProvider(
            api_key=self.api_key,
            publishable_key=self.publishable_key,
            webhook_secret=self.webhook_secret,
        )


type PostPaymentProvider = PostMockPaymentProvider | PostStripePaymentProvider


class PostPaymentOption(BaseModel):
    name: str
    description: str
    provider: PostPaymentProvider

    def to_db_model(self) -> PaymentOption:
        record = self.provider.to_db_model()
        record.name = self.name
        record.description = self.description
        return record


@payments_router.post("/providers")
def post_provider(
    provider: PostPaymentOption,
    _=Depends(authorized([PermissionCategory.PAYMENT], PermissionTier.manager)),
) -> AdminReadPaymentOption:
    with database.with_transaction() as session:
        record = provider.to_db_model()
        session.add(record)
    return AdminReadPaymentOption.from_db_model(record)


# --- /payments ---


class CreateDonation(BaseModel):
    amount: int


@payments_router.get("", response_model=list[ReadPayment])
def list_payments(
    payments: Annotated[PaymentsModule, Depends(PaymentsModule)],
) -> list[ReadPayment]:
    # TODO: permissions
    return [ReadPayment.from_payment(payment) for payment in payments.list_payments()]


@payments_router.get("/payments/{payment_id}")
def get_payment(
    payment_id: UUID, payments: Annotated[PaymentsModule, Depends(PaymentsModule)]
) -> ReadPayment:
    try:
        return ReadPayment.from_payment(payments.get_payment(payment_id))
    except PaymentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@payments_router.post("/payments/donate")
def create_donation(
    body: CreateDonation,
    payments: Annotated[PaymentsModule, Depends(PaymentsModule)],
    user_id: Annotated[int | None, Depends(user_id)],
) -> ReadPayment:
    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    with database.get_session() as session:
        product = DonationProduct(
            user_id=user_id,
            amount=body.amount,
            currency="usd",  # TODO: currency,
        )
        session.add(product)
        session.commit()
        session.flush()
        return ReadPayment.from_payment(Payment.from_db_model(product))


# --- /payments/{payment_id}/transactions ---


class CreateTransaction(BaseModel):
    provider_id: UUID
    payment_id: UUID


class ReadTransaction(BaseModel):
    id: UUID
    payment_id: UUID
    data: TransactionTypes

    @staticmethod
    def from_transaction(transaction: Transaction) -> ReadTransaction:
        return ReadTransaction(
            id=transaction.id, payment_id=transaction.payment_id, data=transaction.data
        )


@payments_router.post("/transactions")
def create_transaction(
    body: CreateTransaction,
    payments: Annotated[PaymentsModule, Depends(PaymentsModule)],
    user_id: Annotated[int | None, Depends(user_id)],
) -> ReadTransaction:
    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    try:
        return ReadTransaction.from_transaction(
            payments.create_transaction(user_id, body.payment_id, body.provider_id)
        )
    except PaymentProviderError:
        raise HTTPException(400, "No such payment provider")
    except PaymentNotFoundError:
        raise HTTPException(404, "No such payment")
    except PaymentNotYoursError:
        raise HTTPException(400, "Not your payment")
    except PaymentAlreadyComplete:
        raise HTTPException(400, "Payment already complete")
    except TransactionInProgressError:
        raise HTTPException(400, "Transaction in progress already")

@payments_router.get("/transactions/{transaction_id}")
def get_transaction(
    transaction_id: UUID,
    payments: Annotated[PaymentsModule, Depends(PaymentsModule)],
    user_id: Annotated[int | None, Depends(user_id)]
) -> ReadTransaction:
    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    try:
        return ReadTransaction.from_transaction(
            payments.get_transaction(user_id, transaction_id)
        )
    except TransactionNotFoundError:
        raise HTTPException(404, "Transaction not found")
    except PaymentNotYoursError:
        raise HTTPException(400, "Not your payment")

@payments_router.post("/transactions/{transaction_id}/confirm")
def confirm_transaction(
    transaction_id: UUID,
    payments: Annotated[PaymentsModule, Depends(PaymentsModule)],
    user_id: Annotated[int | None, Depends(user_id)],
):
    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    try:
        payments.confirm_transaction(transaction_id)
    except PaymentAlreadyComplete:
        return # Treat an already completed payment as a success
    except TransactionNotFoundError:
        raise HTTPException(404, "Transaction not found")
    except TransactionNotSuccessful:
        raise HTTPException(400, "Transaction incomplete")


# --- /providers ---


class ReadPaymentOption(BaseModel):
    id: UUID
    name: str
    description: str
    provider: PaymentProviderType

    @staticmethod
    def from_db_model(option: PaymentOption) -> ReadPaymentOption:
        return ReadPaymentOption(
            id=option.id,
            name=option.name,
            description=option.description,
            provider=option.provider,
        )


@payments_router.get("/providers")
def get_providers() -> list[ReadPaymentOption]:
    with database.get_session() as session:
        return list(map(ReadPaymentOption.from_db_model, session.query(PaymentOption)))
