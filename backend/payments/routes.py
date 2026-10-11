from typing import Annotated, Literal
import typing
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, HTTPException

from auth_module import user_id
from utils.module_config import BaseModel, get_module_config, set_module_config
from database.types import Currency
from .config import PaymentOption, PaymentModuleConfig
from .providers import ServiceName
from .payment import ReadPayment
from .products import DonationProduct
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
    CurrencyConversionError,
)


payments_router = APIRouter(prefix="/payments", tags=["payments", "admin"])

# --- /config ---


class PatchPaymentModuleConfig(BaseModel):
    payment_options: dict[UUID | Literal["new"], PaymentOption] | None = None


class ReadPaymentModuleConfig(BaseModel):
    payment_options: dict[UUID, PaymentOption]

    @staticmethod
    def from_model(config: PaymentModuleConfig) -> ReadPaymentModuleConfig:
        return ReadPaymentModuleConfig(payment_options=config.payment_options)


@payments_router.patch("/config")
def update_config(
    patch: PatchPaymentModuleConfig,
) -> ReadPaymentModuleConfig:
    config = get_module_config(PaymentModuleConfig)
    if patch.payment_options is not None:
        # Process "new" payment provider
        if "new" in patch.payment_options:
            patch.payment_options[uuid.uuid4()] = patch.payment_options.pop("new")
        payment_options = typing.cast(dict[UUID, PaymentOption], patch.payment_options)

        config.payment_options = payment_options
    set_module_config(config)
    return ReadPaymentModuleConfig.from_model(config)


@payments_router.get("/config")
def get_config() -> ReadPaymentModuleConfig:
    config = get_module_config(PaymentModuleConfig)

    return ReadPaymentModuleConfig.from_model(config)


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

    try:
        return ReadPayment.from_payment(
            payments.create_payment(
                user_id=user_id,
                amount=body.amount,
                product=DonationProduct(),
            )
        )
    except CurrencyConversionError:
        raise HTTPException(503, "Failed to convert currency")


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
    service_name: ServiceName

    @staticmethod
    def from_payment_option(uuid: UUID, option: PaymentOption) -> ReadPaymentOption:
        return ReadPaymentOption(
            id=uuid,
            name=option.name,
            description=option.description,
            service_name=option.provider.service_name,
        )


@payments_router.get("/providers")
def get_providers() -> list[ReadPaymentOption]:
    config = get_module_config(PaymentModuleConfig)

    return [
        ReadPaymentOption.from_payment_option(uuid, option)
        for uuid, option in config.payment_options.items()
    ]

# --- /currency ---

class ReadCurrency(BaseModel):
    currency: Currency
    supported_currencies: list[Currency] = list(Currency)

class UpdateCurrency(BaseModel):
    currency: Currency

@payments_router.get("/currency")
def get_currency(
    payments: Annotated[PaymentsModule, Depends(PaymentsModule)],
    user_id: Annotated[int | None, Depends(user_id)],
) -> ReadCurrency:
    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    return ReadCurrency(currency=payments.get_currency(user_id))

@payments_router.put("/currency")
def set_currency(
    body: UpdateCurrency,
    payments: Annotated[PaymentsModule, Depends(PaymentsModule)],
    user_id: Annotated[int | None, Depends(user_id)],
) -> ReadCurrency:
    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    payments.set_currency(user_id, body.currency)
    return ReadCurrency(currency=body.currency)