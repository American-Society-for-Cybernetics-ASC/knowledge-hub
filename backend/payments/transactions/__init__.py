from abc import abstractmethod
from utils import BaseModel

class TransactionInterface(BaseModel):
    @abstractmethod
    def amount(self) -> int: ...
