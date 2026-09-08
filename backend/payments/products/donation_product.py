from typing import Literal

from pydantic import Field

from ._interface import ProductInterface


class DonationProduct(ProductInterface):
    product: Literal["donation"] = Field(default="donation")

    def handle_successful_payment(self):
        pass  # TODO
