from typing import Literal
from pydantic import Field

from payments.transactions import TransactionInterface, TransactionStatus


class MockTransaction(TransactionInterface):
    transaction_type: Literal["mock"] = Field(default="mock")

    def check_status(self) -> TransactionStatus:
        return TransactionStatus.SUCCEEDED
