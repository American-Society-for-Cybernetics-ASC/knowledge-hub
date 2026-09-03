from typing import Annotated, Union

from pydantic import Field

from ._interface import PaymentProviderInterface as PaymentProviderInterface
from .mock_provider import MockPaymentProvider
from .stripe_provider import StripePaymentProvider

type PaymentProviderTypes = Annotated[
    Union[MockPaymentProvider, StripePaymentProvider],
    Field(discriminator="service_name"),
]
"""
Update this union to add new payment provider types. Make sure all members implement :class:`~PaymentProviderInterface`

Make sure your subclass has class variable `service_name: Literal[discriminant]`
where discriminant is a unique string literal (see :class:`~StripePaymentProvider`).
"""
