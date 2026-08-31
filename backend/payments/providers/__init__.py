from abc import abstractmethod
from pydantic import BaseModel
from payments.transactions import TransactionInterface

class PaymentProviderInterface(BaseModel):
    @abstractmethod
    def create_one_off(self, amount: int) -> TransactionInterface: ...