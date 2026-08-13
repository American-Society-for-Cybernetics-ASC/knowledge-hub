from typing import Annotated, Literal, Union

from pydantic import Field
from utils import BaseModel, ModuleConfig
from uuid import UUID

from payments.payment_providers.stripe_provider import StripePaymentProvider
from payments.transactions.mock_transaction import MockTransaction
from payments.transactions.stripe_transaction import StripeTransaction
from payments.enums import PaymentStatus

type TransactionTypes = Annotated[
    Union[StripeTransaction, MockTransaction], Field(discriminator="transaction_type")
]
"""
Update this union to add new transaction types. Make sure all members implement :class:`~payments.transactions.TransactionInterface`

Make sure your subclass has class variable `transaction_type: Literal[discriminant]`
where discriminant is a unique string literal (see :class:`~payments.transactions.stripe_transaction.StripeTransaction`).
"""

type PaymentProviderTypes = Annotated[
    Union[StripePaymentProvider], Field(discriminator="provider_type")
]
"""
Update this union to add new payment provider types. Make sure all members implement :class:`~payments.payment_providers.PaymentProviderInterface`

Make sure your subclass has class variable `provider_type: Literal[discriminant]`
where discriminant is a unique string literal (see :class:`~payments.payment_providers.stripe_provider.StripePaymentProvider`).
"""


class Payment(BaseModel):
    id: UUID
    member_id: UUID

    status: PaymentStatus
    transaction: TransactionTypes


class PaymentModuleConfig(ModuleConfig):
    provider: PaymentProviderTypes | Literal["disabled"]

    @staticmethod
    def module_id() -> str:
        return "payments"

    @staticmethod
    def default() -> PaymentModuleConfig:
        return PaymentModuleConfig(provider="disabled")
