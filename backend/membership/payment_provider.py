from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

class PaymentStatus(str, Enum):
    PAID = "Paid"
    IN_PROGRESS = "InProgress"
    LAPSED = "Lapsed"
    REFUNDED = "Refunded"
 
 
class PaymentProvider(ABC):
    @abstractmethod
    def create_one_off(self) -> dict[str, Any]:
        raise NotImplementedError
 
    @abstractmethod
    def create_recurring(self) -> dict[str, Any]:
        raise NotImplementedError
 
    @abstractmethod
    def check(self, info: dict[str, Any]) -> PaymentStatus:
        raise NotImplementedError
 
 
class StubPaymentProvider(PaymentProvider):
    """Always succeeds — lets you build and test the Membership module
    end-to-end without a working Stripe integration."""
 
    def create_one_off(self) -> dict[str, Any]:
        return {"status": PaymentStatus.PAID.value}
 
    def create_recurring(self) -> dict[str, Any]:
        return {"status": PaymentStatus.PAID.value}
 
    def check(self, info: dict[str, Any]) -> PaymentStatus:
        return PaymentStatus.PAID