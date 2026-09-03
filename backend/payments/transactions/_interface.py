from abc import abstractmethod
from enum import Enum
from utils import BaseModel


class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TransactionInterface(BaseModel):
    @abstractmethod
    def check_status(self) -> TransactionStatus: ...
