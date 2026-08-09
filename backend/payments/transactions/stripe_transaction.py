from typing import Literal
from pydantic import Field

from stripe import PaymentIntent

from payments.transactions import TransactionInterface
from payments.enums import PaymentStatus
from settings import SETTINGS

STATUS_MAP = {
    "requires_payment_method": PaymentStatus.PENDING,
    "requires_confirmation": PaymentStatus.PENDING,
    "required_action": PaymentStatus.PENDING,
    "processing": PaymentStatus.PENDING,
    "requires_capture": PaymentStatus.PENDING,
    "succeeded": PaymentStatus.SUCCEEDED,
    "canceled": PaymentStatus.FAILED
}

class StripeTransaction(TransactionInterface):
    """Interface for a Stripe Transaction"""
    transaction_type: Literal["stripe"] = Field(default="stripe")

    payment_id: str
    amount_value: int
    currency: str = "usd"

    @staticmethod
    def create_one_off(amount: int, currency: str = "usd") -> "StripeTransaction":
        if not SETTINGS.stripe_api_key:
            raise PermissionError(
                "Creating a StripeTransaction without a configured Stripe API key"
            )

        intent: PaymentIntent = PaymentIntent.create(
            amount = amount,
            currency = currency,
            automatic_payment_methods = {"enabled": True}
        )

        return StripeTransaction(
            payment_id = intent.id,
            amount_value = amount,
            currency = currency
        )

    def check(self) -> PaymentStatus:
        intent = PaymentIntent.retrieve(self.payment_id)
        return STATUS_MAP.get(intent.status, PaymentStatus.FAILED)

    def amount(self) -> int:
        return self.amount_value
