from typing import Annotated, Union
from uuid import UUID

from pydantic import Field, TypeAdapter

from utils import BaseModel
from .mock_transaction import MockTransaction
from .stripe_transaction import StripeTransaction
from database import model as dbmodel

type TransactionTypes = Annotated[
    Union[StripeTransaction, MockTransaction], Field(discriminator="transaction_type")
]
"""
Update this union to add new transaction types. Make sure all members implement :class:`~TransactionInterface`

Make sure your subclass has class variable `transaction_type: Literal[discriminant]`
where discriminant is a unique string literal (see :class:`~StripeTransaction`).
"""


class Transaction(BaseModel):
    id: UUID
    payment_id: UUID
    data: TransactionTypes

    @staticmethod
    def from_db_model(model: dbmodel.Transaction) -> Transaction:
        return Transaction(
            id=model.id,
            payment_id=model.payment_id,
            data=TypeAdapter[TransactionTypes](TransactionTypes).validate_json(
                model.data
            ),
        )
