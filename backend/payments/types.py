from pydantic import Field
from typing import Annotated, Union

from payments.provider.stripe_provider import StripeTransaction
from payments.provider.mock_provider import MockTransaction

type TransactionTypes = Annotated[Union[StripeTransaction, MockTransaction], Field(discriminator="transaction_type")]