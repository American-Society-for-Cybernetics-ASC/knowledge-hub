from payments.products import ProductTypes


def handle_successful_payment(product: ProductTypes):
    match product.product:
        case "donation":
            pass  # TODO
