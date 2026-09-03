from decimal import Decimal

from pydantic import TypeAdapter

from utils import BaseModel
from enum import Enum
from uuid import UUID
from datetime import datetime

from .products import ProductTypes
import database.model as dbmodel


class Payment(BaseModel):
    id: UUID
    user_id: UUID
    time: datetime
    amount: Decimal
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
            product=TypeAdapter[ProductTypes](ProductTypes).validate_python(
                model.product
            ),
        )


class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
