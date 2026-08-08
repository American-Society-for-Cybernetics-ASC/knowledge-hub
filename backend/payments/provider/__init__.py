from abc import abstractmethod
from pydantic import BaseModel

from payments.model import PaymentStatus

class PaymentProviderInterface(BaseModel):
    @abstractmethod
    def create_one_off(self, amount: int) -> "PaymentProviderInterface": ...

    @abstractmethod
    def check(self) -> PaymentStatus: ...

    @abstractmethod
    def amount(self) -> int: ...

class TransactionInterface(BaseModel):
    @abstractmethod
    def check(self) -> PaymentStatus: ...

    @abstractmethod
    def amount(self) -> int: ...