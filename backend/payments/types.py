from pydantic import Field
from typing import Annotated, Union

from backend.payments.transactions.stripe_transaction import StripeTransaction
from backend.payments.transactions.mock_transaction import MockTransaction

type TransactionTypes = Annotated[Union[StripeTransaction, MockTransaction], Field(discriminator="transaction_type")]