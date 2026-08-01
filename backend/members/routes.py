from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from members.model import MemberProfile, ProfileUpdate
from members.module import MemberNotFoundError, MembersModule

members_router = APIRouter(prefix="/members", tags=["members"])

def get_current_member_id() -> int:
    """
    Resolve the authenticated user to their member ID.

    Will replace this with the authentication dependency once session login
    has been implemented. 
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not implemented",
    )

# GET /members/me
@members_router.get("/me", response_model=MemberProfile)
def get_my_profile(
    member_id: Annotated[int, Depends(get_current_member_id)],
    module: Annotated[MembersModule, Depends(MembersModule)],
) -> MemberProfile:
    try:
        return module.get_profile(member_id)
    except MemberNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        ) from None

# PATCH /members/me
@members_router.patch("/me", response_model=MemberProfile)
def update_my_profile(
    update: ProfileUpdate,
    member_id: Annotated[int, Depends(get_current_member_id)],
    module: Annotated[MembersModule, Depends(MembersModule)],
) -> MemberProfile:
    try:
        return module.update_profile(member_id, update)
    except MemberNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        ) from None
    
