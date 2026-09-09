from typing import Literal
from pydantic import Field

from database.types import TransactionStatus
from ._interface import TransactionInterface


class MockTransaction(TransactionInterface):
    transaction_type: Literal["mock"] = Field(default="mock")

    def check_status(self) -> TransactionStatus:
        return TransactionStatus.SUCCEEDED
