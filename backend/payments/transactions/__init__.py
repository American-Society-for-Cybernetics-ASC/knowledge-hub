from abc import abstractmethod
from pydantic import BaseModel

from payments.enums import PaymentStatus

class TransactionInterface(BaseModel):
    @abstractmethod
    def check(self) -> PaymentStatus: ...

    @abstractmethod
    def amount(self) -> int: ...
