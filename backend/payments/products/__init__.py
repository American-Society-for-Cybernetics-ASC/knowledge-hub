from typing import Annotated, Union

from pydantic import Field

from ._interface import ProductInterface as ProductInterface
from .membership_product import MembershipProduct

type ProductTypes = Annotated[
    Union[MembershipProduct],
    Field(discriminator="product"),
]
"""
Update this union to add new payment product types. Make sure all members implement :class:`~ProductInterface`

Make sure your subclass has class variable `product: Literal[discriminant]`
where discriminant is a unique string literal (see :class:`~MembershipProduct`).
"""
