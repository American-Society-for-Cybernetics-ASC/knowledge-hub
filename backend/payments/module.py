import os
from typing import Annotated, Optional, Union
from pydantic import BaseModel, Field
from sqlalchemy.exc import NoResultFound
import database

import stripe

from database import model, Session
from payments.providers.mock_provider import MockPaymentProvider
from payments.providers.stripe_provider import StripePaymentProvider

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
                    config= PaymentsModuleConfig.default().model_dump(),
                )
                session.add(config_record)
                session.commit()
                return self.get_config()

    def create_one_off(self, amount: int) -> None:
        """Attempt to create a one-off payment."""

        config = self.get_config()

        if config.provider:
            try:
                config.provider.create_one_off(amount)
                return
            except Exception as e:
                error = str(e)
        else:
            error = "No email provider configured"