from __future__ import annotations
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from auth_module import user_id
from .exceptions import (
    AlreadyAMemberError,
    MembershipTypeOutOfDateError,
    NotAMemberError,
)
from .model import ReadMember
from payments.payment import ReadPayment
from utils import BaseModel
from .module import MembershipModule

membership_router = APIRouter(prefix="/membership", tags=["membership"])


class StartMembership(BaseModel):
    application_id: int


@membership_router.post("/purchase")
def purchase_membership(
    body: StartMembership,
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


class UpdateMembership(BaseModel):
    application_id: int


@membership_router.post("/update")
def update_membership(
    body: StartMembership,
    user_id: Annotated[int | None, Depends(user_id)],
    module: MembershipModule = Depends(MembershipModule),
):
    """Change your membership type"""

    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    try:
        module.update_membership_type(body.application_id, user_id)
    except NotAMemberError:
        raise HTTPException(400, "Not a member")


@membership_router.get("")
def get_membership(
    user_id: Annotated[int | None, Depends(user_id)],
    module: MembershipModule = Depends(MembershipModule),
) -> ReadMember:
    """View single membership's status, tier and payment info"""

    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    member = module.get_member(user_id)

    if not member:
        raise HTTPException(400, "Not a member")

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
