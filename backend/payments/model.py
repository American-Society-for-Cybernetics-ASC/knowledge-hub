from typing import Optional
from utils import BaseModel
from uuid import UUID
from enum import Enum
from pydantic import Field

class PaymentProvider(Enum):
    STRIPE = "stripe"

class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

class Payment(BaseModel):
    id: UUID
    member_id: UUID

    provider: PaymentProvider
    status: PaymentStatus
    
    data: dict

class PaymentData(BaseModel):
    amount: int # Value in the smallest unit of the current currency
    currency: str

    provider_reference: Optional[str] = None

    idempotency_key: str

    data: dict[str, str] = Field(default_factory = dict)

