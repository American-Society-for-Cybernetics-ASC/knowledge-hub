from abc import abstractmethod
from pydantic import BaseModel
from typing import Optional

from model import PaymentStatus

class PaymentProviderInterface(BaseModel):
    @abstractmethod
    def create_one_off(
        self,
        amount: int,
        currency: str,
        customer_id: str,
        data: Optional[dict[str, str]] = None,
        idempotency_key: Optional[str] = None
        ) -> dict: ...

    @abstractmethod
    def create_recurring(self) -> dict: ...

    @abstractmethod
    def check(self, info: dict) -> PaymentStatus: ...