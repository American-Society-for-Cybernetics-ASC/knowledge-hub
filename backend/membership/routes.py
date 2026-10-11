from __future__ import annotations
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from auth_module import authorized, user_id
from auth_module.model import PermissionTier
from database.types import PermissionCategory
from database import get_session, model as dbmodel
from .exceptions import (
    AlreadyAMemberError,
    MembershipTypeNotFoundError,
    MembershipTypeOutOfDateError,
    NotAMemberError,
)
from payments.exceptions import CurrencyConversionError
from .model import MemberStatus, MemberType, ReadMember
from payments.payment import ReadPayment
from utils import BaseModel
from .module import MembershipModule

membership_router = APIRouter(prefix="/membership", tags=["membership"])


class PurchaseMembership(BaseModel):
    application_id: int


@membership_router.post("/purchase")
def purchase_membership(
    body: PurchaseMembership,
    user_id: Annotated[int | None, Depends(user_id)],
    module: MembershipModule = Depends(MembershipModule),
) -> ReadPayment:
    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    try:
        return ReadPayment.from_payment(
            module.purchase_create_membership(body.application_id, user_id)
        )
    except AlreadyAMemberError:
        raise HTTPException(400, "Already a member")
    except CurrencyConversionError:
        raise HTTPException(503, "Failed to convert currency")


@membership_router.post("/renew")
def renew_membership(
    user_id: Annotated[int | None, Depends(user_id)],
    module: MembershipModule = Depends(MembershipModule),
) -> ReadPayment:
    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    try:
        return ReadPayment.from_payment(module.purchase_renew_membership(user_id))
    except NotAMemberError:
        raise HTTPException(400, "Not a member")
    except MembershipTypeOutOfDateError:
        raise HTTPException(
            400,
            "Your membership type is no longer supported: please reapply for a new membership type",
        )
    except CurrencyConversionError:
            raise HTTPException(503, "Failed to convert currency")


class UpdateMembership(BaseModel):
    application_id: int


@membership_router.post("/update")
def update_membership(
    body: PurchaseMembership,
    user_id: Annotated[int | None, Depends(user_id)],
    module: MembershipModule = Depends(MembershipModule),
):
    """Change your membership type"""

    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    try:
        module.set_members_type(body.application_id, user_id)
    except NotAMemberError:
        raise HTTPException(400, "Not a member")


@membership_router.get("")
def get_membership(
    user_id: Annotated[int | None, Depends(user_id)],
    module: MembershipModule = Depends(MembershipModule),
) -> ReadMember | None:
    """View single membership's status, tier and payment info"""

    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    member = module.get_member(user_id)

    if not member:
        return None

    return ReadMember.from_member(member)


@membership_router.post("/cancel")
def cancel_membership(
    user_id: Annotated[int | None, Depends(user_id)],
    module: MembershipModule = Depends(MembershipModule),
):
    """Cancels a membership"""
    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    try:
        module.cancel_membership(user_id)
    except NotAMemberError:
        raise HTTPException(400, "Not a member")


@membership_router.post("/uncancel")
def uncancel_membership(
    user_id: Annotated[int | None, Depends(user_id)],
    module: MembershipModule = Depends(MembershipModule),
):
    """Reinstates a previously cancelled membership (REQ-1.5)."""
    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    try:
        module.uncancel_membership(user_id)
    except NotAMemberError:
        raise HTTPException(400, "Not a member")


class MembershipSummary(BaseModel):
    email: str
    display_name: str
    due_date: datetime
    member_type: str | None
    status: MemberStatus
    cancelled: bool


@membership_router.get("/admin/members")
def get_memberships(
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> list[MembershipSummary]:
    with get_session() as session:
        return [
            MembershipSummary(
                email=db_member.auth_user.email,
                display_name=db_member.auth_user.name or db_member.auth_user.email,
                due_date=db_member.due_date,
                member_type=db_member.member_type.name
                if db_member.member_type is not None
                else None,
                status=MemberStatus.calc_expiry(db_member.due_date),
                cancelled=db_member.cancelled,
            )
            for db_member in session.query(dbmodel.Member)
        ]


@membership_router.get("/member_type")
def membership_types() -> list[MemberType]:
    with get_session() as session:
        return [
            MemberType.from_db_model(record)
            for record in session.query(dbmodel.MemberType)
        ]


class PostMembershipType(BaseModel):
    name: str
    price: int


@membership_router.post("/member_type")
def create_member_type(
    body: PostMembershipType,
    module: MembershipModule = Depends(MembershipModule),
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> MemberType:
    return module.create_member_type(body.name, body.price)


class PatchMembershipType(BaseModel):
    name: str | None = None
    price: int | None = None


@membership_router.patch("/member_type/{member_type_id}")
def patch_membership_type(
    member_type_id: UUID,
    patch: PatchMembershipType,
    module: MembershipModule = Depends(MembershipModule),
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> MemberType:
    try:
        return module.update_member_type(
            member_type_id, name=patch.name, price=patch.price
        )
    except MembershipTypeNotFoundError:
        raise HTTPException(404, "Member type not found")
