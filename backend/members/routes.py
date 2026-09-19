from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from members.model import MemberProfile, MemberSearchResult, ProfileUpdate
from members.module import MemberNotFoundError, MembersModule
import database
from auth_module import user_id as get_authenticated_user_id
from database import model

members_router = APIRouter(prefix="/members", tags=["member-profiles"])


def get_current_member_id(
    auth_user_id: Annotated[int, Depends(get_authenticated_user_id)],
) -> int:
    """Resolve the authenticated user to their member ID."""

    if auth_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

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

        return member.auth_user_id


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


# GET /members?q=<search query>
@members_router.get("", response_model=list[MemberSearchResult])
def search_members(
    q: Annotated[str, Query(min_length=1, max_length=100)],
    _: Annotated[int, Depends(get_current_member_id)],
    module: Annotated[MembersModule, Depends(MembersModule)],
) -> list[MemberSearchResult]:
    """Search currnet member profiles by display name, tag or affiliation."""
    return module.search_members(q)[:50]


# GET /members/{member_id}
@members_router.get("/{member_id}", response_model=MemberProfile)
def get_member_profile(
    member_id: int,
    # Require the caller to be an authenticated member
    _: Annotated[int, Depends(get_current_member_id)],
    module: Annotated[MembersModule, Depends(MembersModule)],
) -> MemberProfile:
    try:
        return module.get_profile(member_id)
    except MemberNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        ) from None

