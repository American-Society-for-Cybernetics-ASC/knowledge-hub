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

membership_router = APIRouter(prefix="/membership", tags=["membership"])


@membership_router.post("", response_model=MembershipRead, status_code=201)
def start_membership(
    data: MembershipCreate,
    module: MembershipModule = Depends(MembershipModule),
):
    """Start a membership for an approved member"""
    return module.start_membership(data)


@membership_router.get("", response_model=MembershipListResult)
def list_memberships(
    params: MembershipListParams = Depends(),
    module: MembershipModule = Depends(MembershipModule),
):
    """Lists memberships"""
    memberships, total = module.list_memberships(params)
    return MembershipListResult(
        memberships=[MembershipRead.model_validate_sqlalchemy(m) for m in memberships],
        total=total,
    )


@membership_router.get("/{membership_id}", response_model=MembershipRead)
def get_membership(
    membership_id: int,
    module: MembershipModule = Depends(MembershipModule),
):
    """View single membership's status, tier and payment info"""
    return module.get_membership(membership_id)


@membership_router.post(
    "/{membership_id}/cancel", response_model=MembershipActionResult
)
def cancel_membership(
    membership_id: int,
    module: MembershipModule = Depends(MembershipModule),
):
    """Cancels a memberhsip"""
    membership = module.cancel_membership(membership_id)
    return MembershipActionResult(
        membership=MembershipRead.model_validate_sqlalchemy(membership),
        message="Membership cancelled.",
    )


@membership_router.post(
    "/{membership_id}/uncancel", response_model=MembershipActionResult
)
def uncancel_membership(
    membership_id: int,
    module: MembershipModule = Depends(MembershipModule),
):
    """Reinstates a previously cancelled membership (REQ-1.5)."""
    membership = module.uncancel_membership(membership_id)
    return MembershipActionResult(
        membership=MembershipRead.model_validate_sqlalchemy(membership),
        message="Membership reinstated.",
    )
