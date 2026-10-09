import uuid

from fastapi.testclient import TestClient
import pytest

from payments.routes import (
    PostMockPaymentProvider,
    PostPaymentOption,
    PostStripePaymentProvider,
)
from database.products import DonationProduct

from .conftest import TEST_USER_ID
from payments.payment import PaymentStatus, Payment
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


@pytest.fixture()
def mock_stripe_transaction(monkeypatch, mock_payment):
    with monkeypatch.context() as m:
        m.setattr(
            "payments.transactions.stripe_transaction.PaymentIntent.create", mock_create
        )
        yield StripeTransaction.create_one_off(mock_payment)


@pytest.fixture()
def mock_payment(mock_get_session) -> Payment:
    with mock_get_session() as session:
        product = DonationProduct(user_id=TEST_USER_ID, amount=10010, currency="usd")
        session.add(product)
        session.commit()
        session.flush()
        return Payment.from_db_model(product)


def test_config(test_server: TestClient):
    response = test_server.post(
        "/payments/providers",
        json=PostPaymentOption(
            name="example",
            description="example provider",
            provider=PostMockPaymentProvider(),
        ).model_dump(mode="json"),
    )

    assert response.status_code == 200

    response = test_server.get("/payments/providers")
    assert response.status_code == 200
    assert response.json()[0]["provider"] == "mock"


def test_donation(test_server: TestClient):
    response = test_server.post("/payments/payments/donate", json={"amount": 10010})
    assert response.status_code == 200
    assert "id" in response.json()

    response = test_server.get(f"/payments/payments/{response.json()['id']}")
    assert response.status_code == 200
    assert response.json()["amount"] == 10010
    assert response.json()["product_description"] == "Donation"


def test_transaction(
    test_server, mock_payment_provider: uuid.UUID, mock_payment: Payment
):
    response = test_server.post(
        "/payments/transactions",
        json={
            "provider_id": str(mock_payment_provider),
            "payment_id": str(mock_payment.id),
        },
    )
    assert response.status_code == 200
    assert "id" in response.json()

    id = response.json()["id"]
    response = test_server.post(
        f"/payments/transactions/{id}/confirm",
    )
    assert response.status_code == 200

    response = test_server.get(
        f"/payments/payments/{str(mock_payment.id)}",
    )
    assert response.status_code == 200
    assert response.json()["status"] == PaymentStatus.SUCCEEDED


def test_repeat_transactions_fail(
    test_server, mock_payment_provider: uuid.UUID, mock_payment: Payment
):
    response = test_server.post(
        "/payments/transactions",
        json={
            "provider_id": str(mock_payment_provider),
            "payment_id": str(mock_payment.id),
        },
    )
    assert response.status_code == 200
    assert "id" in response.json()
    id = response.json()["id"]

    # Currently in progress
    response = test_server.post(
        "/payments/transactions",
        json={
            "provider_id": str(mock_payment_provider),
            "payment_id": str(mock_payment.id),
        },
    )
    assert response.status_code == 400

    response = test_server.post(
        f"/payments/transactions/{id}/confirm",
    )
    assert response.status_code == 200

    # Already succeeded
    response = test_server.post(
        "/payments/transactions",
        json={
            "provider_id": str(mock_payment_provider),
            "payment_id": str(mock_payment.id),
        },
    )
    assert response.status_code == 400


# Stripe Transaction Tests


def test_stripe_create_one_off_calls_stripe_with_parameters(
    monkeypatch, mock_payment: Payment
):
    calls = {}

    def mock_create_and_record(**kwargs):
        calls.update(kwargs)
        return MockPaymentIntent(id="pi_test_id")

    with monkeypatch.context() as m:
        m.setattr(
            "payments.transactions.stripe_transaction.PaymentIntent.create",
            mock_create_and_record,
        )

        transaction = StripeTransaction.create_one_off(mock_payment)

        assert calls == {
            "amount": 10010,
            "currency": mock_payment.currency,
            "automatic_payment_methods": {"enabled": True},
        }
        assert transaction.payment_id == "pi_test_id"


def test_stripe_check_always_calls_stripe(monkeypatch, mock_stripe_transaction):
    call_count = 0

    def mock_retrieve_and_count(payment_id):
        nonlocal call_count
        call_count += 1
        return MockPaymentIntent(status="pending")

    monkeypatch.setattr(
        "payments.transactions.stripe_transaction.PaymentIntent.retrieve",
        mock_retrieve_and_count,
    )

    mock_stripe_transaction.check_status()
    mock_stripe_transaction.check_status()

    assert call_count == 2


# Stripe Payment Provider Tests


def test_stripe_provider_create_one_off_returns_stripe_transaction(
    monkeypatch, test_server, mock_payment
):
    with monkeypatch.context() as m:
        m.setattr(
            "payments.transactions.stripe_transaction.PaymentIntent.create", mock_create
        )

        response = test_server.post(
            "/payments/providers",
            json=PostPaymentOption(
                name="example",
                description="example provider",
                provider=PostStripePaymentProvider(
                    api_key="", publishable_key="", webhook_secret=""
                ),
            ).model_dump(mode="json"),
        )
        assert response.status_code == 200
        provider_id = response.json()["id"]

        response = test_server.post(
            "/payments/transactions",
            json={"provider_id": str(provider_id), "payment_id": str(mock_payment.id)},
        )
        assert response.status_code == 200
        assert response.json()["data"]["transaction_type"] == "stripe"
