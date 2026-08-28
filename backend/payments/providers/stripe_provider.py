from typing import Literal
from uuid import uuid4

from stripe import PaymentIntent

from payments.providers import PaymentProviderInterface
from payments.transactions.stripe_transaction import StripeTransaction
from payments.transactions import PaymentStatus

class StripePaymentProvider(PaymentProviderInterface):
    """
    The Payment Provider Class for Stripe. Contains the configuration for Stripe payments and handles the creation of a StripeTransaction.
    """
    currency: str = "usd"

    def create_one_off(self, amount: int) -> "StripeTransaction":
        intent = PaymentIntent.create(
            amount = amount,
            currency = self.currency,
            automatic_payment_methods = {"enabled": True}
        )

        return StripeTransaction(
            payment_id = intent.id,
            amount_value = amount,
            currency = self.currency
        )