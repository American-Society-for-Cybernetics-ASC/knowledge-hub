from typing import Literal
from pydantic import Field

from stripe import PaymentIntent
from database.types import TransactionStatus
from ._interface import TransactionInterface
from payments.payment import Payment
from payments.exceptions import PaymentError

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

    payment_id: str  # Stripe PaymentIntent id
    client_secret: str  # Allows frontend Stripe elements to complete PaymentIntent

    @staticmethod
    def create_one_off(payment: Payment) -> StripeTransaction:
        intent: PaymentIntent = PaymentIntent.create(
            amount=payment.amount,
            currency=payment.currency,
            automatic_payment_methods={"enabled": True},
        )

        # Must validate client_secret as it is a nullable value
        if intent.client_secret is None:
            raise PaymentError("Payment Intent did not return a valid client secret")

        return StripeTransaction(
            payment_id=intent.id, client_secret=intent.client_secret
        )

    def check_status(self) -> TransactionStatus:
        intent = PaymentIntent.retrieve(self.payment_id)
        return STATUS_MAP.get(intent.status, TransactionStatus.FAILED)
