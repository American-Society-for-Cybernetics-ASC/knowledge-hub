from typing import Annotated
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from utils import BaseModel

from payments.module import PaymentsModule
from payments.exceptions import NoProviderConfiguredError, PaymentProviderError, PaymentNotFoundError
from payments.transactions.mock_transaction import MockTransaction
from payments.transactions.stripe_transaction import StripeTransaction

payments_router = APIRouter(prefix="/payments", tags=["payments"])

class PaymentRequest(BaseModel):
    member_id: UUID
    amount: int

class PaymentResponse(BaseModel):
    payment_id: int
    date: datetime
    status: str
    kind: str
    transaction: MockTransaction | StripeTransaction


def get_payments_module() -> PaymentsModule:
    return PaymentsModule()

@payments_router.get("/{payment_id}", response_model = PaymentResponse)
def get_payment(payment_id: int, payments: Annotated[PaymentsModule, Depends(get_payments_module)]):
    try:
        return payments.get_payment(payment_id)
    except PaymentNotFoundError as e:
        raise HTTPException(status_code = 404, detail = str(e))

@payments_router.get("", response_model = list[PaymentResponse])
def list_payments(payments: Annotated[PaymentsModule, Depends(get_payments_module)]):
    return payments.list_payments()

@payments_router.post("", response_model = PaymentResponse)
def create_payment(body: PaymentRequest, payments: Annotated[PaymentsModule, Depends(get_payments_module)]):
    try:
        return payments.create_one_off(body.amount)
    except NoProviderConfiguredError as e:
        raise HTTPException(status_code = 409, detail = str(e))
    except PaymentProviderError as e:
        raise HTTPException(status_code = 502, detail = str(e))