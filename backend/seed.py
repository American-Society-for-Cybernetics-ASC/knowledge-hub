import sys

from payments.config import PaymentModuleConfig, PaymentOption
from payments.providers.mock_provider import MockPaymentProvider
from payments.providers.stripe_provider import StripePaymentProvider
from utils.module_config import get_module_config, set_module_config
from settings import SETTINGS


def build_mock_option() -> PaymentOption:
    return PaymentOption(
        name="Mock",
        description="Test payment provider",
        provider=MockPaymentProvider(),
    )


def build_stripe_option() -> PaymentOption:
    return PaymentOption(
        name="Stripe",
        description="Stripe payment provider",
        provider=StripePaymentProvider(
            api_key=SETTINGS.stripe_api_key or "",
            publishable_key=SETTINGS.stripe_publishable_key or "",
            webhook_secret=SETTINGS.stripe_webhook_secret or "",
        ),
    )


PROVIDER_BUILDERS = {
    "mock": build_mock_option,
    "stripe": build_stripe_option,
}


def main():
    args = sys.argv[1:]
    names = [name.lower() for arg in args for name in arg.split()]

    if not names:
        print("Usage: seed.py <provider> [<provider> ...]")
        sys.exit(1)

    payment_options = [PROVIDER_BUILDERS[name]() for name in names]

    get_module_config(PaymentModuleConfig)

    config = PaymentModuleConfig(payment_options=payment_options)

    set_module_config(config)


if __name__ == "__main__":
    main()
