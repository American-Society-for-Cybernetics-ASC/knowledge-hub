from typing import Annotated
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from payments.module import PaymentsModule
from payments.model import Payment
from payments.exceptions import NoProviderConfiguredError, PaymentProviderError

payments_router = APIRouter(prefix="/payments", tags=["payments"])

class PaymentRequest(BaseModel):
    member_id: UUID
    amount: int

class PaymentResponse(BaseModel):
    payment_id: int
    amount: int
    date: datetime
    status: str
    kind: str
    provider: str
    external_id: str

    model_config = {"from_attributes": True}


def get_payments_module() -> PaymentsModule:
    return PaymentsModule()

@payments_router.post("", response_model=PaymentResponse)
def create_payment(body: PaymentRequest, payments: Annotated[PaymentsModule, Depends(get_payments_module)]):
    try:
        return payments.create_one_off(body.amount)
    except NoProviderConfiguredError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except PaymentProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))