from typing import Literal

from fastapi import APIRouter

from utils import BaseModel, get_module_config, set_module_config
from payments.model import PaymentModuleConfig, PaymentProviderTypes


payments_router = APIRouter(prefix="/payments", tags=["payments", "admin"])

# --- Admin ---


class PatchPaymentModuleConfig(BaseModel):
    provider: PaymentProviderTypes | Literal["disabled"] | None = None


class ReadPaymentModuleConfig(BaseModel):
    provider: PaymentProviderTypes | Literal["disabled"]


@payments_router.patch("/config")
def update_config(
    patch: PatchPaymentModuleConfig,
):
    config = get_module_config(PaymentModuleConfig)
    if patch.provider is not None:
        config.provider = patch.provider
    set_module_config(config)


@payments_router.get("/config")
def get_config() -> ReadPaymentModuleConfig:
    config = get_module_config(PaymentModuleConfig)

    return ReadPaymentModuleConfig(provider=config.provider)
