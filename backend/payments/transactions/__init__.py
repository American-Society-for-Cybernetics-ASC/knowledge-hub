from abc import abstractmethod
from utils import BaseModel

from payments.enums import PaymentStatus


class TransactionInterface(BaseModel):
    @abstractmethod
    def check(self) -> PaymentStatus: ...

    @abstractmethod
    def amount(self) -> int: ...
