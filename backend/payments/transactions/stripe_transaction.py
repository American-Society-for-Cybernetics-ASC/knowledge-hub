from typing import Literal
from pydantic import Field

from stripe import PaymentIntent
from database.types import TransactionStatus
from ._interface import TransactionInterface
from payments.payment import Payment

STATUS_MAP = {
    "requires_payment_method": TransactionStatus.PENDING,
    "requires_confirmation": TransactionStatus.PENDING,
    "requires_action": TransactionStatus.PENDING,
    "processing": TransactionStatus.PENDING,
    "requires_capture": TransactionStatus.PENDING,
    "succeeded": TransactionStatus.SUCCEEDED,
    "canceled": TransactionStatus.FAILED,
}


class StripeTransaction(TransactionInterface):
    """Interface for a Stripe Transaction"""

    transaction_type: Literal["stripe"] = Field(default="stripe")

    payment_id: str

    @staticmethod
    def create_one_off(payment: Payment) -> StripeTransaction:
        intent: PaymentIntent = PaymentIntent.create(
            amount=payment.amount,
            currency=payment.currency,
            automatic_payment_methods={"enabled": True},
        )

        return StripeTransaction(payment_id=intent.id)

    def check_status(self) -> TransactionStatus:
        intent = PaymentIntent.retrieve(self.payment_id)
        return STATUS_MAP.get(intent.status, TransactionStatus.FAILED)
