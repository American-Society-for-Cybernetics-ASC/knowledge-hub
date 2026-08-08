from typing import Literal, Optional, Any
from pydantic import Field
from uuid import uuid4

from . import PaymentProviderInterface
from model import PaymentProvider, PaymentStatus, Payment
from settings import SETTINGS

from stripe import PaymentIntent, StripeError, InvalidRequestError

# TODO: Read config inside here

class StripeProvider(PaymentProviderInterface):
    service_name: Literal["stripe"] = Field(default = "stripe")

    def create_one_off(
        self, 
        amount: int, 
        currency: str, 
        customer_id: str, 
        metadata: Optional[dict[str, str]] = None, 
        idempotency_key: Optional[str] = None
        ) -> dict[str, Any]:
        """Create a Payment Intent and return its intermediate details and secrets. This payment Intent is unconfirmed."""
        if not SETTINGS.stripe_api_key:
            raise PermissionError(
                "Using StripeProvider without a configured Stripe API key"
            )

        try:
            intent = PaymentIntent.create(
                amount = amount,
                currency = currency,
                customer = customer_id,
                automatic_payment_methods = {"enabled": True},
                metadata = metadata or {},
                idempotency_key = idempotency_key or str(uuid4())
            )

            return {
                "provider_reference": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency
            }
        except StripeError as e:
            # TODO Simplify Error Details
            raise RuntimeError(f"StripeError occurred while creating a one-off payment: {e}") 
        

    def create_recurring(self) -> dict:
        raise NotImplementedError

    def check(self, info: dict[str, Any]) -> PaymentStatus:
        """Check the status of a Stripe Payment, returning its associated :class:`~model.PaymentStatus`"""
        try:
            if "payment_intent_id" not in info:
                raise ValueError("No payment_intent_id provided in info")

            intent = PaymentIntent.retrieve(info["payment_intent_id"])

            return self._get_payment_intent_status(intent.status)
        
        except InvalidRequestError as e:
            raise RuntimeError(f"Stripe reference is invalid: {e}")
        except StripeError as e:
            raise RuntimeError(f"StripeError occurred while checking payment status: {e}")

    @staticmethod
    def _get_payment_intent_status(stripe_status: str) -> PaymentStatus:
        status_map = {
            "requires_payment_method": PaymentStatus.PENDING,
            "requires_confirmation": PaymentStatus.PENDING,
            "required_action": PaymentStatus.PENDING,
            "processing": PaymentStatus.PENDING,
            "requires_capture": PaymentStatus.PENDING,
            "succeeded": PaymentStatus.SUCCEEDED,
            "canceled": PaymentStatus.FAILED
        }
        return status_map.get(stripe_status, PaymentStatus.FAILED)