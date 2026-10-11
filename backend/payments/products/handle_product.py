from sqlalchemy.orm import Session

from payments.products import ProductTypes


def handle_successful_payment(session: Session, product: ProductTypes):
    from membership import membership_module

    match product.product:
        case "create_membership":
            membership_module.create_membership(
                session, product.membership_type_id, product.user_id, product.duration
            )
        case "renew_membership":
            membership_module.renew_membership(
                session, product.user_id, product.duration
            )
        case "donation":
            pass  # TODO
