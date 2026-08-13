from typing import Literal

from pydantic import Field

from payments.transactions.stripe_transaction import StripeTransaction
from utils import BaseModel


class StripePaymentProvider(BaseModel):
    provider_type: Literal["stripe"] = Field(default="stripe")
    stripe_api_key: str

    def create_one_off(self, amount: int, currency: str = "usd") -> StripeTransaction:
        return StripeTransaction.create_one_off(amount, currency)
