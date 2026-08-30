from typing import Literal

from pydantic import Field

from payments.transactions.stripe_transaction import StripeTransaction
from utils import BaseModel


class StripePaymentProvider(BaseModel):
    provider_type: Literal["stripe"] = Field(default="stripe")
    api_key: str
    publishable_key: str
    webhook_secret: str

    def create_one_off(self, amount: int, currency: str = "usd") -> StripeTransaction:
        return StripeTransaction.create_one_off(amount, currency)
