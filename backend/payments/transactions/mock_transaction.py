from typing import Literal
from pydantic import Field
from uuid import uuid4

from payments.transactions import TransactionInterface
from payments.enums import PaymentStatus


class MockTransaction(TransactionInterface):
    transaction_type: Literal["mock"] = Field(default="mock")

    payment_id: str
    amount_value: int
    status: PaymentStatus = PaymentStatus.SUCCEEDED

    @staticmethod
    def create_one_off(
        amount: int, *, force_status: PaymentStatus = PaymentStatus.SUCCEEDED
    ) -> "MockTransaction":
        return MockTransaction(
            payment_id=uuid4().hex[:12], amount_value=amount, status=force_status
        )

    def check(self) -> PaymentStatus:
        return self.status

    def amount(self) -> int:
        return self.amount_value
