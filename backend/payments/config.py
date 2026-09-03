from pydantic import Field

from utils import BaseModel
from utils.module_config import ModuleConfig
from .providers import PaymentProviderTypes


class PaymentOption(BaseModel):
    name: str = Field(min_length=1, max_length=16)
    description: str = Field(min_length=1, max_length=100)
    provider: PaymentProviderTypes


class PaymentModuleConfig(ModuleConfig):
    payment_options: list[PaymentOption]

    @staticmethod
    def module_id() -> str:
        return "payments"

    @staticmethod
    def default() -> PaymentModuleConfig:
        return PaymentModuleConfig(payment_options=[])
