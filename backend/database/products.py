import datetime
from typing import override
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.types import ProductType

from .model import MemberType, Payment


class DonationProduct(Payment):
    IDENTITY = ProductType.DONATION
    __tablename__ = "product_" + IDENTITY
    id: Mapped[uuid.UUID] = mapped_column(ForeignKey(Payment.id), primary_key=True)

    @override
    def product_description(self):
        return "Donation"

    __mapper_args__ = {
        "polymorphic_identity": IDENTITY,
    }


class CreateMembershipProduct(Payment):
    IDENTITY = ProductType.CREATE_MEMBERSHIP
    __tablename__ = "product_" + IDENTITY
    id: Mapped[uuid.UUID] = mapped_column(ForeignKey(Payment.id), primary_key=True)
    duration: Mapped[datetime.timedelta]
    member_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(MemberType.id))

    member_type: Mapped[MemberType] = relationship(
        "MemberType", foreign_keys=[member_type_id], lazy="joined"
    )

    @override
    def product_description(self):
        return f"Created Membership as '{self.member_type}'"

    __mapper_args__ = {
        "polymorphic_identity": IDENTITY,
    }


class RenewMembershipProduct(Payment):
    IDENTITY = ProductType.RENEW_MEMBERSHIP
    __tablename__ = "product_" + IDENTITY

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey(Payment.id), primary_key=True)
    duration: Mapped[datetime.timedelta]
    member_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(MemberType.id))

    member_type: Mapped[MemberType] = relationship(
        "MemberType", foreign_keys=[member_type_id], lazy="joined"
    )

    @override
    def product_description(self):
        return f"Renewed Membership as '{self.member_type}'"

    __mapper_args__ = {
        "polymorphic_identity": IDENTITY,
    }
