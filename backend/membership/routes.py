from __future__ import annotations
from fastapi import APIRouter, Depends

from .module import MembershipModule
from .schema import (
    MembershipActionResult,
    MembershipCreate,
    MembershipListParams,
    MembershipListResult,
    MembershipRead,
)

membership_router = APIRouter(prefix="/membership", tags=["Membership"])

@membership_router.post("", response_model=MembershipRead, status_code=201)
def start_membership(
    data: MembershipCreate,
    module: MembershipModule = Depends(MembershipModule),
):
    return module.start_membership(data)
 
 
@membership_router.get("", response_model=MembershipListResult)
def list_memberships(
    params: MembershipListParams = Depends(),
    module: MembershipModule = Depends(MembershipModule),
):
    memberships, total = module.list_memberships(params)
    return MembershipListResult(memberships=memberships, total=total)
 
 
@membership_router.get("/{membership_id}", response_model=MembershipRead)
def get_membership(
    membership_id: int,
    module: MembershipModule = Depends(MembershipModule),
):
    return module.get_membership(membership_id)
 
 
@membership_router.post("/{membership_id}/cancel", response_model=MembershipActionResult)
def cancel_membership(
    membership_id: int,
    module: MembershipModule = Depends(MembershipModule),
):
    membership = module.cancel_membership(membership_id)
    return MembershipActionResult(membership=membership, message="Membership cancelled.")
 
 
@membership_router.post("/{membership_id}/uncancel", response_model=MembershipActionResult)
def uncancel_membership(
    membership_id: int,
    module: MembershipModule = Depends(MembershipModule),
):
    membership = module.uncancel_membership(membership_id)
    return MembershipActionResult(membership=membership, message="Membership reinstated.")