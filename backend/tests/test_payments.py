from payments.enums import PaymentStatus
from payments.transactions.mock_transaction import MockTransaction
from payments.transactions.stripe_transaction import StripeTransaction

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
        "payments.transactions.stripe_transaction.SETTINGS.stripe_api_key",
        "sk_test_key",
    )
    monkeypatch.setattr(
        "payments.transactions.stripe_transaction.PaymentIntent.create", mock_create
    )
    return StripeTransaction.create_one_off(amount)


# Mock Transaction Tests


def test_mock_create_one_off_has_succeeded_default():
    transaction = MockTransaction.create_one_off(100)

    assert transaction.amount() == 100
    assert transaction.check() == PaymentStatus.SUCCEEDED


def test_mock_create_one_off_generates_unique_payment_id():
    transaction_a = MockTransaction.create_one_off(100)
    transaction_b = MockTransaction.create_one_off(100)

    assert transaction_a.payment_id != transaction_b.payment_id


def test_mock_create_one_off_with_forced_status():
    transaction = MockTransaction.create_one_off(100, force_status=PaymentStatus.FAILED)

    assert transaction.check() == PaymentStatus.FAILED


def test_mock_amount_matches_input():
    transaction = MockTransaction.create_one_off(100)

    assert transaction.amount() == 100


def test_mock_transaction_data_is_consistent():
    transaction = MockTransaction.create_one_off(
        100, force_status=PaymentStatus.PENDING
    )

    assert transaction.check() == PaymentStatus.PENDING
    assert transaction.check() == PaymentStatus.PENDING


# Stripe Transaction Tests


def test_stripe_create_one_off_calls_stripe_with_parameters(monkeypatch):
    calls = {}

    def mock_create_and_record(**kwargs):
        calls.update(kwargs)
        return MockPaymentIntent(id="pi_test_id")

    monkeypatch.setattr(
        "payments.transactions.stripe_transaction.SETTINGS.stripe_api_key",
        "sk_test_key",
    )
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
