import uuid

from database.model import PaymentOption
from database.types import PaymentProviderType

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class MockPaymentProvider(PaymentOption):
    _IDENTITY = PaymentProviderType.MOCK
    __tablename__ = "payment_provider_" + _IDENTITY

    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(PaymentOption.id), primary_key=True
    )

    __mapper_args__ = {
        "polymorphic_identity": _IDENTITY,
    }


class StripePaymentProvider(PaymentOption):
    _IDENTITY = PaymentProviderType.STRIPE
    __tablename__ = "payment_provider_" + _IDENTITY

    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(PaymentOption.id), primary_key=True
    )
    api_key: Mapped[str]
    publishable_key: Mapped[str]
    webhook_secret: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": _IDENTITY,
    }
