from utils import BaseModel
from uuid import UUID

from payments.types import TransactionTypes
from payments.enums import PaymentStatus


class Payment(BaseModel):
    id: UUID
    member_id: UUID

    status: PaymentStatus
    transaction: TransactionTypes
