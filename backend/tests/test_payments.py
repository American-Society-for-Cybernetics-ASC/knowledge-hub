from payments.enums import PaymentStatus
from payments.transactions.mock_transaction import MockTransaction
from payments.transactions.stripe_transaction import StripeTransaction
from payments.providers.mock_provider import MockPaymentProvider
from payments.providers.stripe_provider import StripePaymentProvider

# Test Resources


class MockPaymentIntent:
    def __init__(self, id: str = "", status: str = "") -> None:
        self.id = id
        self.status = status


def mock_create(**kwargs):
    return MockPaymentIntent(id="pi_test_id")


def mock_retrieve(payment_id):
    return MockPaymentIntent(status="pending")


def mock_stripe_transaction(monkeypatch, amount=100):
    monkeypatch.setattr(
        "payments.transactions.stripe_transaction.PaymentIntent.create", mock_create
    )
    return StripeTransaction.create_one_off(amount)


# Mock Transaction Tests

def test_mock_amount_matches_input():
    transaction = MockTransaction.create_one_off(100)

    assert transaction.amount() == 100


def test_mock_transaction_data_is_consistent():
    transaction = MockTransaction.create_one_off(
        100
    )

    assert transaction.amount() == 100
    assert transaction.amount() == 100


# Stripe Transaction Tests

def test_stripe_create_one_off_calls_stripe_with_parameters(monkeypatch):
    calls = {}

    def mock_create_and_record(**kwargs):
        calls.update(kwargs)
        return MockPaymentIntent(id="pi_test_id")

    monkeypatch.setattr(
        "payments.transactions.stripe_transaction.PaymentIntent.create",
        mock_create_and_record,
    )

    transaction = StripeTransaction.create_one_off(100, currency="usd")

    assert calls == {
        "amount": 100,
        "currency": "usd",
        "automatic_payment_methods": {"enabled": True},
    }
    assert transaction.payment_id == "pi_test_id"


def test_stripe_create_one_off_has_usd_currency_default(monkeypatch):
    transaction = mock_stripe_transaction(monkeypatch, amount=100)

    assert transaction.currency == "usd"


def test_stripe_amount_matches_input(monkeypatch):
    transaction = mock_stripe_transaction(monkeypatch, amount=100)

    assert transaction.amount() == 100


def test_stripe_check_always_calls_stripe(monkeypatch):
    transaction = mock_stripe_transaction(monkeypatch)

    call_count = 0

    def mock_retrieve_and_count(payment_id):
        nonlocal call_count
        call_count += 1
        return MockPaymentIntent(status="pending")

    monkeypatch.setattr(
        "payments.transactions.stripe_transaction.PaymentIntent.retrieve",
        mock_retrieve_and_count,
    )

    transaction.check()
    transaction.check()

    assert call_count == 2

# Stripe Payment Provider Tests

def test_stripe_provider_create_one_off_returns_stripe_transaction(monkeypatch):
    monkeypatch.setattr("payments.transactions.stripe_transaction.PaymentIntent.create", mock_create)

    provider = StripePaymentProvider(api_key="", publishable_key="", webhook_secret="")

    transaction = provider.create_one_off(100)

    assert isinstance(transaction, StripeTransaction)
    assert transaction.payment_id == "pi_test_id"
    assert transaction.amount() == 100

def test_stripe_provider_passes_amount_to_stripe(monkeypatch):
    calls = {}

    def mock_create_and_record(**kwargs):
        calls.update(kwargs)
        return MockPaymentIntent(id = "pi_test_id")

    monkeypatch.setattr("payments.transactions.stripe_transaction.PaymentIntent.create", mock_create_and_record)

    provider = StripePaymentProvider(api_key="", publishable_key="", webhook_secret="")

    provider.create_one_off(100)

    assert calls == {
        "amount": 100,
        "currency": "usd",
        "automatic_payment_methods": {"enabled": True}
    }