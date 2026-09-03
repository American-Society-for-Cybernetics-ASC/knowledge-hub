from typing import Literal

from pydantic import Field

from membership.module import MembershipModule
from ._interface import ProductInterface


class MembershipProduct(ProductInterface):
    product: Literal["membership"] = Field(default="membership")
    membership_id: int

    def handle_successful_payment(self):
        MembershipModule().renew_membership(self.membership_id)
