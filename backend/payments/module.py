import os
from uuid import UUID

import stripe
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from .handle_provider import handle_create_transaction
from .handle_product import handle_successful_payment
import database
from database.types import PaymentStatus, TransactionStatus
from database import model
from .payment import Payment
from .transactions import Transaction
from .currency import Currency, convert_currency
from .exceptions import (
    PaymentNotYoursError,
    PaymentProviderNotFoundError,
    PaymentNotFoundError,
    PaymentAlreadyComplete,
    TransactionInProgressError,
    TransactionNotFoundError,
    TransactionNotSuccessful,
)

stripe.api_key = os.environ.get("STRIPE_API_KEY", "")


class PaymentsModule:
    def add_payment(
        self, session: Session, payment: model.Payment
    ) -> Payment:
        """
        Save a new product as a payment in the user's selected currency. Free payments immediately succeed.

        :parameter payment: a product with 'amount' in the smallest unit of the base currency (e.g. cents for usd)
        :raises CurrencyConversionError:
        """
        currency = session.get_one(model.AuthUser, payment.user_id).currency
        payment.currency = currency
        if payment.amount == 0:
            payment.status = PaymentStatus.SUCCEEDED
        else:
            payment.amount = convert_currency(payment.amount, currency)
        
        with session.begin_nested():
            session.add(payment)

        if payment.status == PaymentStatus.SUCCEEDED:
            handle_successful_payment(session, payment)

        return Payment.from_db_model(payment)

    def create_transaction(
        self, user_id: int, payment_id: UUID, provider_id: UUID
    ) -> Transaction:
        """
        :raises BadPaymentProviderError: if provider_id is invalid
        :raises PaymentNotFoundError: if payment_id is not found
        :raises PaymentNotYoursError: if user_id doesn't match payment_id
        :raises PaymentAlreadyComplete:
        :raises TransactionInProgressError:
        """
        with database.get_session() as session:
            payment_option = session.get(model.PaymentOption, provider_id)

            if not payment_option:
                raise PaymentProviderNotFoundError(
                    "The requested payment provider doesn't currently exist"
                )

            payment = self.get_payment(payment_id)

            if payment.user_id != user_id:
                raise PaymentNotYoursError()

            if payment.status != PaymentStatus.PENDING:
                raise PaymentAlreadyComplete()

            for transaction in (
                session.query(model.Transaction)
                .where(model.Transaction.payment_id == payment.id)
                .where(model.Transaction.last_known_status == TransactionStatus.PENDING)
            ):
                transaction.last_known_status = Transaction.from_db_model(
                    transaction
                ).data.check_status()
                if transaction.last_known_status != TransactionStatus.FAILED:
                    raise TransactionInProgressError()

            data = handle_create_transaction(payment, payment_option)

            record = model.Transaction(
                payment_id=payment_id, data=data.model_dump(mode="json")
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return Transaction.from_db_model(record)

    def confirm_transaction(self, transaction_id: UUID):
        """
        :raises TransactionNotFoundError:
        :raises TransactionNotSuccessful:
        :raises PaymentAlreadyComplete:
        """
        complete_product: model.Payment | None = None
        with database.with_transaction() as session:
            try:
                transaction_record = session.get_one(model.Transaction, transaction_id)
            except NoResultFound:
                raise TransactionNotFoundError()

            # Foreign key constraint
            payment_record = session.get_one(
                model.Payment, transaction_record.payment_id
            )

            if payment_record.status != PaymentStatus.PENDING:
                raise PaymentAlreadyComplete()

            transaction_record.last_known_status = Transaction.from_db_model(
                transaction_record
            ).data.check_status()
            if transaction_record.last_known_status == TransactionStatus.SUCCEEDED:
                payment_record.status = PaymentStatus.SUCCEEDED
                complete_product = payment_record
            else:
                raise TransactionNotSuccessful()

            if complete_product:
                handle_successful_payment(session, complete_product)

    def get_transaction(self, user_id: int, transaction_id: UUID) -> Transaction:
        """
        :raises TransactionNotFoundError:
        :raises PaymentNotYoursError: if the transaction's payment is not owned by user_id
        """
        with database.get_session() as session:
            try:
                record = session.get_one(model.Transaction, transaction_id)
            except NoResultFound:
                raise TransactionNotFoundError()
            
            payment_record = session.get_one(model.Payment, record.payment_id)
            if payment_record.user_id != user_id:
                raise PaymentNotYoursError()

            return Transaction.from_db_model(record)

    def get_payment(self, payment_id: UUID) -> Payment:
        """:raises PaymentNotFoundError:"""
        with database.get_session() as session:
            try:
                return Payment.from_db_model(session.get_one(model.Payment, payment_id))
            except NoResultFound:
                raise PaymentNotFoundError(f"No payment with id {payment_id}")

    def list_payments(self) -> list[Payment]:
        with database.get_session() as session:
            query = session.query(model.Payment)
            return [Payment.from_db_model(model) for model in query]

    def get_currency(self, user_id: int) -> Currency:
        with database.get_session() as session:
            return session.get_one(model.AuthUser, user_id).currency

    def set_currency(self, user_id: int, currency: Currency):
        with database.get_session() as session:
            session.get_one(model.AuthUser, user_id).currency = currency
            session.commit()
