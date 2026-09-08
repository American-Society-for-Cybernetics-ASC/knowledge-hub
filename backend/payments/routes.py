from typing import Annotated
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from utils.module_config import BaseModel, get_module_config, set_module_config
from .config import PaymentOption, PaymentModuleConfig
from payments.module import PaymentsModule
from payments.exceptions import (
    NoProviderConfiguredError,
    PaymentProviderError,
    PaymentNotFoundError,
)
from payments.transactions.mock_transaction import MockTransaction
from payments.transactions.stripe_transaction import StripeTransaction


payments_router = APIRouter(prefix="/payments", tags=["payments", "admin"])

# --- Admin ---


class PatchPaymentModuleConfig(BaseModel):
    payment_options: list[PaymentOption] | None = None


class ReadPaymentModuleConfig(BaseModel):
    payment_options: list[PaymentOption]

    @staticmethod
    def from_model(config: PaymentModuleConfig) -> ReadPaymentModuleConfig:
        return ReadPaymentModuleConfig(payment_options=config.payment_options)


@payments_router.patch("/config")
def update_config(
    patch: PatchPaymentModuleConfig,
) -> ReadPaymentModuleConfig:
    config = get_module_config(PaymentModuleConfig)
    if patch.payment_options is not None:
        config.payment_options = patch.payment_options
    set_module_config(config)
    return ReadPaymentModuleConfig.from_model(config)


@payments_router.get("/config")
def get_config() -> ReadPaymentModuleConfig:
    config = get_module_config(PaymentModuleConfig)

    return ReadPaymentModuleConfig.from_model(config)


# --- Payments Module ---


class PaymentRequest(BaseModel):
    member_id: UUID
    amount: int


class PaymentResponse(BaseModel):
    payment_id: int
    date: datetime
    status: str
    kind: str
    transaction: MockTransaction | StripeTransaction


@payments_router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int, payments: Annotated[PaymentsModule, Depends(PaymentsModule)]
):
    try:
        return payments.get_payment(payment_id)
    except PaymentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@payments_router.get("", response_model=list[PaymentResponse])
def list_payments(payments: Annotated[PaymentsModule, Depends(PaymentsModule)]):
    return payments.list_payments()


@payments_router.post("", response_model=PaymentResponse)
def create_payment(
    body: PaymentRequest, payments: Annotated[PaymentsModule, Depends(PaymentsModule)]
):
    try:
        return payments.create_one_off(body.amount)
    except NoProviderConfiguredError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except PaymentProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))
