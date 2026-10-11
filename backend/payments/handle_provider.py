from payments.transactions._interface import TransactionInterface
from payments.transactions.mock_transaction import MockTransaction
from database.payment_providers import MockPaymentProvider, StripePaymentProvider
from payments.transactions.stripe_transaction import StripeTransaction
from database.types import PaymentProviderType
import database
import database.model
from payments.payment import Payment


def handle_create_transaction(
    payment: Payment, provider: database.model.PaymentOption
) -> TransactionInterface:
    match provider.provider:
        case PaymentProviderType.STRIPE:
            assert isinstance(provider, StripePaymentProvider)
            return StripeTransaction.create_one_off(payment)
        case PaymentProviderType.MOCK:
            assert isinstance(provider, MockPaymentProvider)
            return MockTransaction()
