import os
from typing import Annotated, Union
from pydantic import BaseModel, Field
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timezone

import stripe

import database
from database import model
from utils import get_module_config
from payments.model import PaymentModuleConfig
from payments.providers.mock_provider import MockPaymentProvider
from payments.providers.stripe_provider import StripePaymentProvider
from payments.transactions import PaymentStatus
from payments.exceptions import NoProviderConfiguredError, PaymentProviderError, PaymentNotFoundError

stripe.api_key = os.environ.get("STRIPE_API_KEY", "")

type PaymentProvider = Annotated[
    Union[MockPaymentProvider, StripePaymentProvider], Field(discriminator="service_name")
]

class PaymentsModule():
    MODULE_ID = "payments"

    def create_one_off(self, amount: int) -> model.Payment:
        """Attempt to create a one-off payment."""

        config = get_module_config(PaymentModuleConfig)

        if not config.payment_options:
            raise NoProviderConfiguredError("Attempting to create payment intent without a configured payment provider")

        provider = config.payment_options[0].provider # TODO: Allow for payment options to be selected
        
        try:
            transaction = provider.create_one_off(amount)
        except Exception as e:
            raise PaymentProviderError(e) from e

        with database.get_session() as session:
            record = model.Payment(
                date = datetime.now(timezone.utc),
                status = PaymentStatus.PENDING.value,
                kind = "one-off",
                transaction = transaction.model_dump(mode="json")
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def get_payment(self, payment_id: int) -> model.Payment:
        with database.get_session() as session:
            try:
                return session.get_one(model.Payment, payment_id)
            except NoResultFound:
                raise PaymentNotFoundError(f"No payment with id {payment_id}")

    def list_payments(self) -> list[model.Payment]:
        with database.get_session() as session:
            query = session.query(model.Payment)
            return query.all()