from typing import Literal
from uuid import uuid4

from providers import PaymentProviderInterface
from transactions.mock_transaction import MockTransaction
from transactions import PaymentStatus

class MockPaymentProvider(PaymentProviderInterface):
    def __init__(self, default_status: PaymentStatus = PaymentStatus.SUCCEEDED) -> None:
        self.default_status: PaymentStatus = default_status

    def create_one_off(self, amount: int) -> "MockTransaction":
        return MockTransaction(
            payment_id = uuid4().hex[:12], amount_value = amount, status = self.default_status
        )