from decimal import Decimal
import os
from uuid import UUID
from sqlalchemy.exc import NoResultFound

import stripe

import database
from database import model
from utils.module_config import get_module_config
from .payment import Payment, PaymentStatus
from .transactions import Transaction, TransactionStatus
from .config import PaymentModuleConfig
from .products import ProductTypes
from .exceptions import (
    NoProviderConfiguredError,
    PaymentNotFoundError,
    PaymentAlreadyComplete,
    TransactionNotSuccessful,
)

stripe.api_key = os.environ.get("STRIPE_API_KEY", "")


class PaymentsModule:
    def create_payment(
        self, user_id: int, amount: Decimal, currency: str, product: ProductTypes
    ) -> Payment:
        with database.get_session() as session:
            record = model.Payment(
                user_id=user_id,
                amount=amount,
                currency=currency,
                status=PaymentStatus.PENDING,
                product=product.model_dump_json(),
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return Payment.from_db_model(record)

    def create_transaction(self, payment_id: UUID) -> Transaction:
        config = get_module_config(PaymentModuleConfig)
        if not config.payment_options:
            raise NoProviderConfiguredError(
                "Attempting to create payment intent without a configured payment provider"
            )
        provider = config.payment_options[
            0
        ].provider  # TODO: Allow for payment options to be selected

        with database.get_session() as session:
            payment = Payment.from_db_model(session.get_one(model.Payment, payment_id))

            if payment.status != PaymentStatus.PENDING:
                raise PaymentAlreadyComplete()

            content = provider.create(payment)

            record = model.Transaction(
                payment_id=payment_id, content=content.model_dump_json()
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return Transaction.from_db_model(record)

    def confirm_transaction(self, transaction_id: UUID):
        product: ProductTypes | None = None
        with database.get_session() as session:
            transaction = Transaction.from_db_model(
                session.get_one(model.Transaction, transaction_id)
            )
            payment = Payment.from_db_model(
                session.get_one(model.Payment, transaction.payment_id)
            )
            if payment.status != PaymentStatus.PENDING:
                raise PaymentAlreadyComplete()
            if transaction.data.check_status() == TransactionStatus.SUCCEEDED:
                payment.status = PaymentStatus.SUCCEEDED
                product = payment.product
            else:
                raise TransactionNotSuccessful()

            session.commit()

        if product:
            product.handle_successful_payment()

    def get_payment(self, payment_id: UUID) -> model.Payment:
        with database.get_session() as session:
            try:
                return session.get_one(model.Payment, payment_id)
            except NoResultFound:
                raise PaymentNotFoundError(f"No payment with id {payment_id}")

    def list_payments(self) -> list[model.Payment]:
        with database.get_session() as session:
            query = session.query(model.Payment)
            return query.all()
