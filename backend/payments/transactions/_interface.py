from abc import abstractmethod
from database.types import TransactionStatus
from utils import BaseModel


class TransactionInterface(BaseModel):
    @abstractmethod
    def check_status(self) -> TransactionStatus: ...
