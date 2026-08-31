from abc import abstractmethod
from pydantic import BaseModel

class PaymentProviderInterface(BaseModel):
    @abstractmethod
    def create_one_off(self, amount: int) -> "PaymentProviderInterface": ...