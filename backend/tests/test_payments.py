from payments.provider import PaymentProviderInterface, PaymentStatus
from payments.provider.mock_provider import MockTransaction
from payments.provider.stripe_provider import STATUS_MAP, StripeTransaction

# Mock Transaction Tests

def test_create_one_off_has_succeeded_default():
    transaction = MockTransaction.create_one_off(100)

    assert transaction.amount() == 100
    assert transaction.check() == PaymentStatus.SUCCEEDED

def test_create_one_off_generates_unique_payment_id():
    transaction_a = MockTransaction.create_one_off(100)
    transaction_b = MockTransaction.create_one_off(100)

    assert transaction_a.payment_id != transaction_b.payment_id

def test_create_one_off_with_forced_status():
    transaction = MockTransaction.create_one_off(100, force_status = PaymentStatus.FAILED)

    assert transaction.check() == PaymentStatus.FAILED

def test_amount_matches_input():
    transaction = MockTransaction.create_one_off(100)

    assert transaction.amount == 100

def test_transaction_data_is_consistent():
    transaction = MockTransaction.create_one_off(100, force_status = PaymentStatus.PENDING)

    assert transaction.check() == PaymentStatus.PENDING
    assert transaction.check() == PaymentStatus.PENDING