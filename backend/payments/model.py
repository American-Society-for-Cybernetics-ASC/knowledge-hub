from utils import BaseModel
from uuid import UUID
from datetime import datetime

from payments.types import TransactionTypes
from payments.enums import PaymentStatus


class Payment(BaseModel):
    id: UUID
    member_id: UUID

    date: datetime
    status: PaymentStatus
    transaction: TransactionTypes
