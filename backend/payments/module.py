import os
from uuid import UUID

import stripe
from sqlalchemy.exc import NoResultFound


from .products.handle_product import handle_successful_payment
import database
from database.types import PaymentStatus, TransactionStatus
from database import model
from utils.module_config import get_module_config
from .payment import Payment
from .transactions import Transaction
from .config import PaymentModuleConfig
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
        config = get_module_config(PaymentModuleConfig)

        payment_option = config.payment_options.get(provider_id)
        if not payment_option:
            raise PaymentProviderNotFoundError(
                "The requested payment provider doesn't currently exist"
            )

        payment = self.get_payment(payment_id)

        if payment.user_id != user_id:
            raise PaymentNotYoursError()

        if payment.status != PaymentStatus.PENDING:
            raise PaymentAlreadyComplete()

        with database.get_session() as session:
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

            data = payment_option.provider.create(payment)

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
