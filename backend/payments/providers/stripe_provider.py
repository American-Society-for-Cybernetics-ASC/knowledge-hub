from typing import Literal
from pydantic import Field

from payments.payment import Payment
from payments.providers import PaymentProviderInterface
from payments.transactions.stripe_transaction import StripeTransaction


class StripePaymentProvider(PaymentProviderInterface):
    """The Payment Provider Class for Stripe. Contains the configuration for Stripe payments and handles the creation of a StripeTransaction."""

    service_name: Literal["stripe"] = Field(default="stripe")
    api_key: str
    publishable_key: str
    webhook_secret: str

    def create(self, payment: Payment) -> StripeTransaction:
        return StripeTransaction.create_one_off(payment)
