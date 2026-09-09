from pydantic import TypeAdapter

from uuid import UUID
from datetime import datetime

from .products import ProductTypes
import database.model as dbmodel
from database.types import PaymentStatus
from utils import BaseModel


class Payment(BaseModel):
    id: UUID
    user_id: int
    time: datetime
    amount: int
    currency: str
    status: PaymentStatus
    product: ProductTypes

    @staticmethod
    def from_db_model(model: dbmodel.Payment) -> Payment:
        return Payment(
            id=model.id,
            user_id=model.user_id,
            time=model.time,
            amount=model.amount,
            currency=model.currency,
            status=model.status,
            product=TypeAdapter[ProductTypes](ProductTypes).validate_json(
                model.product
            ),
        )


class ReadPayment(BaseModel):
    id: UUID
    user_id: int
    time: datetime
    amount: int
    currency: str
    status: PaymentStatus
    product: ProductTypes

    @staticmethod
    def from_payment(payment: Payment) -> ReadPayment:
        return ReadPayment(
            id=payment.id,
            user_id=payment.user_id,
            time=payment.time,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            product=payment.product,
        )
