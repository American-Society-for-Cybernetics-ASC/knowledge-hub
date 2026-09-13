from typing import Literal
from pydantic import Field
from uuid import uuid4

from payments.transactions import TransactionInterface

class MockTransaction(TransactionInterface):
    transaction_type: Literal["mock"] = Field(default="mock")

    amount_value: int

    @staticmethod
    def create_one_off(
        amount: int
    ) -> "MockTransaction":
        return MockTransaction(
            amount_value=amount
        )

    def amount(self) -> int:
        return self.amount_value
