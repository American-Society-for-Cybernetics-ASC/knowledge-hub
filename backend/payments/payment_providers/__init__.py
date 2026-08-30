from abc import abstractmethod
from payments.transactions import TransactionInterface
from utils import BaseModel


class PaymentProviderInterface(BaseModel):
    @abstractmethod
    def create_one_off(self, amount: int) -> TransactionInterface: ...
