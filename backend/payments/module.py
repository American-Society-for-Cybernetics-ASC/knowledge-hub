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
    PaymentNotYoursError,
    PaymentProviderNotFoundError,
    PaymentNotFoundError,
    PaymentAlreadyComplete,
    TransactionNotFoundError,
    TransactionNotSuccessful,
)

stripe.api_key = os.environ.get("STRIPE_API_KEY", "")


class PaymentsModule:
    def create_payment(
        self, user_id: int, amount: int, currency: str, product: ProductTypes
    ) -> Payment:
        """
        :parameter amount: in the smallest unit of the currency (e.g. cents for usd)
        """
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

    def create_transaction(
        self, user_id: int, payment_id: UUID, provider_id: UUID
    ) -> Transaction:
        """
        :raises BadPaymentProviderError: if provider_id is invalid
        :raises PaymentNotFoundError: if payment_id is not found
        :raises PaymentNotYoursError: if user_id doesn't match payment_id
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

        with database.get_session() as session:
            if payment.status != PaymentStatus.PENDING:
                raise PaymentAlreadyComplete()

            data = payment_option.provider.create(payment)

            record = model.Transaction(
                payment_id=payment_id, data=data.model_dump_json()
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return Transaction.from_db_model(record)

    def confirm_transaction(self, transaction_id: UUID):
        """
        :raises TransactionNotFoundError:
        :raises TransactionNotSuccessful:
        """
        product: ProductTypes | None = None
        with database.get_session() as session:
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

            if (
                Transaction.from_db_model(transaction_record).data.check_status()
                == TransactionStatus.SUCCEEDED
            ):
                payment_record.status = PaymentStatus.SUCCEEDED
                product = Payment.from_db_model(payment_record).product
            else:
                raise TransactionNotSuccessful()

            session.commit()

        if product:
            product.handle_successful_payment()

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
