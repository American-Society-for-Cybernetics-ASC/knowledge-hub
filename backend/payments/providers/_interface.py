from abc import abstractmethod

from utils import BaseModel
from payments.payment import Payment
from payments.transactions import TransactionInterface


class PaymentProviderInterface(BaseModel):
    @abstractmethod
    def create(self, payment: Payment) -> TransactionInterface: ...
