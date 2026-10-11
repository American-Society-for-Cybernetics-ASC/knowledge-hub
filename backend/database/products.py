import datetime
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.types import ProductType

from .model import MemberType, Payment


class DonationProduct(Payment):
    _IDENTITY = ProductType.DONATION
    __tablename__ = "product_" + _IDENTITY
    id: Mapped[uuid.UUID] = mapped_column(ForeignKey(Payment.id), primary_key=True)

    def product_description(self):
        return "Donation"

    __mapper_args__ = {
        "polymorphic_identity": _IDENTITY,
    }


class CreateMembershipProduct(Payment):
    _IDENTITY = ProductType.CREATE_MEMBERSHIP
    __tablename__ = "product_" + _IDENTITY
    id: Mapped[uuid.UUID] = mapped_column(ForeignKey(Payment.id), primary_key=True)
    duration: Mapped[datetime.timedelta]
    member_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(MemberType.id))

    member_type: Mapped[MemberType] = relationship(
        "MemberType", foreign_keys=[member_type_id], lazy="joined"
    )

    def product_description(self):
        return f"Created Membership as '{self.member_type.name}'"

    __mapper_args__ = {
        "polymorphic_identity": _IDENTITY,
    }


class RenewMembershipProduct(Payment):
    _IDENTITY = ProductType.RENEW_MEMBERSHIP
    __tablename__ = "product_" + _IDENTITY

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey(Payment.id), primary_key=True)
    duration: Mapped[datetime.timedelta]
    member_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(MemberType.id))

    member_type: Mapped[MemberType] = relationship(
        "MemberType", foreign_keys=[member_type_id], lazy="joined"
    )

    def product_description(self):
        return f"Renewed Membership as '{self.member_type.name}'"

    __mapper_args__ = {
        "polymorphic_identity": _IDENTITY,
    }
