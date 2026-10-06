from sqlalchemy.orm import Session

import database
import database.model
import database.products
from database.types import ProductType


def handle_successful_payment(session: Session, payment: database.model.Payment):
    from membership import membership_module

    match payment.product:
        case ProductType.CREATE_MEMBERSHIP:
            assert isinstance(payment, database.products.CreateMembershipProduct)
            membership_module.create_membership(
                session, payment.member_type_id, payment.user_id, payment.duration
            )
        case ProductType.RENEW_MEMBERSHIP:
            assert isinstance(payment, database.products.RenewMembershipProduct)
            membership_module.renew_membership(
                session, payment.user_id, payment.duration
            )
        case ProductType.DONATION:
            pass  # TODO
