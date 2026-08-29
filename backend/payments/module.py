import os
from typing import Annotated, Optional, Union
from pydantic import BaseModel, Field
from sqlalchemy.exc import NoResultFound
from uuid import UUID
from datetime import datetime, timezone

import stripe

import database
from database import model, Session
from payments.providers.mock_provider import MockPaymentProvider
from payments.providers.stripe_provider import StripePaymentProvider
from payments.transactions import TransactionInterface, PaymentStatus
from payments.exceptions import NoProviderConfiguredError, PaymentProviderError

stripe.api_key = os.environ.get("STRIPE_API_KEY", "")

type PaymentProvider = Annotated[
    Union[MockPaymentProvider, StripePaymentProvider], Field(discriminator="service_name")
]

class PaymentsModuleConfig(BaseModel):
    provider: Optional[PaymentProvider]

    @staticmethod
    def default() -> "PaymentsModuleConfig":
        return PaymentsModuleConfig(provider = None)

class PaymentsModule():
    MODULE_ID = "payments"

    def get_config(self) -> PaymentsModuleConfig:
        """Fetch the module's config from the database"""
        with database.get_session() as session:
            try:
                config_record = session.get_one(model.Module, PaymentsModule.MODULE_ID)
                return PaymentsModuleConfig.model_validate(config_record.config)
            except NoResultFound:
                config_record = model.Module(
                    module_name = PaymentsModule.MODULE_ID,
                    config= PaymentsModuleConfig.default().model_dump(mode="json"),
                )
                session.add(config_record)
                session.commit()
                return self.get_config()

    def create_one_off(self, amount: int) -> model.Payment:
        """Attempt to create a one-off payment."""

        config = self.get_config()

        if not config.provider:
            raise NoProviderConfiguredError("Attempting to create payment intent without a configured payment provider")
        
        try:
            transaction = config.provider.create_one_off(amount)
        except Exception as e:
            raise PaymentProviderError(e) from e

        with database.get_session() as session:
            record = model.Payment(
                amount = transaction.amount_value,
                currency = transaction.currency,
                date = datetime.now(timezone.utc),
                status = PaymentStatus.PENDING.value,
                kind = "one-off",
                provider = transaction.provider,
                external_id = transaction.payment_id
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record