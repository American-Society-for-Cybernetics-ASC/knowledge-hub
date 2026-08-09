from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from members.model import MemberProfile, ProfileUpdate
from members.module import MemberNotFoundError, MembersModule
import database
from auth_module import user_id as get_authenticated_user_id
from database import model

members_router = APIRouter(prefix="/members", tags=["member-profiles"])


def get_current_member_id(
    auth_user_id: Annotated[int, Depends(get_authenticated_user_id)],
) -> int:
    """Resolve the authenticated user to their member ID."""

    with database.get_session() as session:
        member = (
            session.query(model.Member)
            .filter(model.Member.auth_user_id == auth_user_id)
            .first()
        )

        if member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member account not found",
            )

        return member.member_id


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
