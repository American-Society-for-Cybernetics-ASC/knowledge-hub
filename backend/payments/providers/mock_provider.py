from typing import Literal
from uuid import uuid4

from payments.providers import PaymentProviderInterface
from payments.transactions.mock_transaction import MockTransaction

class MockPaymentProvider(PaymentProviderInterface):
    service_name: Literal["mock"] = "mock"

    def create_one_off(self, amount: int) -> "MockTransaction":
        return MockTransaction(
            amount_value = amount
        )