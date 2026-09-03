from typing import Literal
from uuid import uuid4

from payments.providers import PaymentProviderInterface
from payments.transactions.mock_transaction import MockTransaction
from payments.transactions import PaymentStatus

class MockPaymentProvider(PaymentProviderInterface):
    service_name: Literal["mock"] = "mock"
    
    default_status: PaymentStatus = PaymentStatus.SUCCEEDED

    def create_one_off(self, amount: int) -> "MockTransaction":
        return MockTransaction(
            payment_id = uuid4().hex[:12], amount_value = amount, status = self.default_status
        )