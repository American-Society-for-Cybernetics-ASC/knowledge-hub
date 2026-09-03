from typing import Literal

from payments.payment import Payment
from payments.providers import PaymentProviderInterface
from payments.transactions.mock_transaction import MockTransaction


class MockPaymentProvider(PaymentProviderInterface):
    service_name: Literal["mock"] = "mock"

    def create(self, payment: Payment) -> "MockTransaction":
        return MockTransaction()
