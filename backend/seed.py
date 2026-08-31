from payments.model import PaymentModuleConfig, PaymentOption
from payments.providers.mock_provider import MockPaymentProvider
from payments.providers.stripe_provider import StripePaymentProvider
from utils import get_module_config, set_module_config
from settings import SETTINGS

get_module_config(PaymentModuleConfig)

config = PaymentModuleConfig(
    payment_options = [
        PaymentOption(
            name = "Stripe",
            description = "Stripe payment provider",
            provider = StripePaymentProvider(
                api_key = SETTINGS.stripe_api_key or "",
                publishable_key = SETTINGS.stripe_publishable_key or "",
                webhook_secret = SETTINGS.stripe_webhook_secret or "",
            ),
        ),
        PaymentOption(
            name = "Mock",
            description = "Test payment provider",
            provider = MockPaymentProvider(),
        ),
    ]
)
set_module_config(config)