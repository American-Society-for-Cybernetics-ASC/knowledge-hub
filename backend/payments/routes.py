from fastapi import APIRouter

from utils import BaseModel, get_module_config, set_module_config
from payments.model import PaymentModuleConfig, PaymentOption


payments_router = APIRouter(prefix="/payments", tags=["payments", "admin"])

# --- Admin ---


class PatchPaymentModuleConfig(BaseModel):
    payment_options: list[PaymentOption] | None = None


class ReadPaymentModuleConfig(BaseModel):
    payment_options: list[PaymentOption]


@payments_router.patch("/config")
def update_config(
    patch: PatchPaymentModuleConfig,
):
    config = get_module_config(PaymentModuleConfig)
    if patch.payment_options is not None:
        config.payment_options = patch.payment_options
    set_module_config(config)


@payments_router.get("/config")
def get_config() -> ReadPaymentModuleConfig:
    config = get_module_config(PaymentModuleConfig)

    return ReadPaymentModuleConfig(payment_options=config.payment_options)
