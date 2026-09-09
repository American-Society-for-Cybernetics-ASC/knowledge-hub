from datetime import timedelta
from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import Field

from utils import BaseModel


class DonationProduct(BaseModel):
    product: Literal["donation"] = Field(default="donation")


class CreateMembershipProduct(BaseModel):
    product: Literal["create_membership"] = Field(default="create_membership")
    user_id: int
    duration: timedelta
    membership_type_id: UUID


class RenewMembershipProduct(BaseModel):
    product: Literal["renew_membership"] = Field(default="renew_membership")
    user_id: int
    duration: timedelta


type ProductTypes = Annotated[
    Union[RenewMembershipProduct | CreateMembershipProduct | DonationProduct],
    Field(discriminator="product"),
]
"""
Update this union to add new payment product types.

Make sure your subclass has class variable `product: Literal[discriminant]`
where discriminant is a unique string literal (see :class:`~MembershipProduct`).
"""
