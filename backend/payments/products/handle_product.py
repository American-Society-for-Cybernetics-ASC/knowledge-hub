from payments.products import ProductTypes


def handle_successful_payment(product: ProductTypes):
    from membership.module import MembershipModule

    match product.product:
        case "create_membership":
            MembershipModule().create_membership(
                product.membership_type_id, product.user_id, product.duration
            )
        case "renew_membership":
            MembershipModule().renew_membership(product.user_id, product.duration)
        case "donation":
            pass  # TODO
