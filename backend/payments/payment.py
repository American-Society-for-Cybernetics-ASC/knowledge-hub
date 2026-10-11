from uuid import UUID
from datetime import datetime

import database.model as dbmodel
from database.types import PaymentStatus, ProductType
from utils import BaseModel


class Payment(BaseModel):
    id: UUID
    user_id: int
    timestamp: datetime
    amount: int
    currency: str
    status: PaymentStatus
    product: ProductType
    product_description: str

    @staticmethod
    def from_db_model(model: dbmodel.Payment) -> Payment:
        return Payment(
            id=model.id,
            user_id=model.user_id,
            timestamp=model.timestamp,
            amount=model.amount,
            currency=model.currency,
            status=model.status,
            product=model.product,
            product_description=model.product_description(),
        )


class ReadPayment(BaseModel):
    id: UUID
    user_id: int
    timestamp: datetime
    amount: int
    currency: str
    status: PaymentStatus
    product: ProductType
    product_description: str

    @staticmethod
    def from_payment(payment: Payment) -> ReadPayment:
        return ReadPayment(
            id=payment.id,
            user_id=payment.user_id,
            timestamp=payment.timestamp,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            product=payment.product,
            product_description=payment.product_description,
        )
