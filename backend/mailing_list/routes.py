from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from .module import MailingListModule, MemberNotFoundError
from .model import MailingList, MailingListMember
from auth_module import authorized, user_id, PermissionTier

mailing_list_router = APIRouter(prefix="/mailing-lists", tags=["mailing-lists"])


@mailing_list_router.get("/")
def get_mailing_lists(
    module: Annotated[MailingListModule, Depends(MailingListModule)],
) -> list[MailingList]:
    return module.get_mailing_lists()


@mailing_list_router.post("/register")
def register_mailing_list(
    mailing_list_email: str,
    module: Annotated[MailingListModule, Depends(MailingListModule)],
    _=Depends(authorized(["groups"], PermissionTier.manager)),
) -> MailingList:
    """Manager register an existing Google Workspace Group"""
    try:
        return module.register_mailing_list(mailing_list_email)
    except Exception:
        raise HTTPException(
            status_code=409,
            detail=f"Mailing list {mailing_list_email} already exists",
        )


@mailing_list_router.post("/{mailing_list_id}/join")
def join_mailing_list(
    mailing_list_id: int,
    member_id: Annotated[int, Depends(user_id)],
    module: Annotated[MailingListModule, Depends(MailingListModule)],
) -> None:
    """join a mailing list"""
    try:
        module.join_mailing_list(mailing_list_id, member_id)
    except MemberNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@mailing_list_router.get("/{mailing_list_id}/members")
def get_mailing_list_members(
    mailing_list_id: int,
    module: Annotated[MailingListModule, Depends(MailingListModule)],
) -> list[MailingListMember]:
    """get a list of all members from a mailing list"""
    return module.get_mailing_list_members(mailing_list_id)


@mailing_list_router.post("/{mailing_list_id}/members/add")
def add_member(
    mailing_list_id: int,
    email: str,
    module: Annotated[MailingListModule, Depends(MailingListModule)],
    _=Depends(authorized(["groups"], PermissionTier.manager)),
) -> None:
    """Manager add a member to a group by email"""
    try:
        module.add_member(mailing_list_id, email)
    except MemberNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@mailing_list_router.post("/{mailing_list_id}/leave")
def leave_mailing_list(
    mailing_list_id: int,
    member_id: Annotated[int, Depends(user_id)],
    module: Annotated[MailingListModule, Depends(MailingListModule)],
) -> None:
    """leave a mailing list"""
    try:
        module.leave_mailing_list(mailing_list_id, member_id)
    except MemberNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@mailing_list_router.post("/{mailing_list_id}/members/kick")
def kick_member(
    mailing_list_id: int,
    email: str,
    module: Annotated[MailingListModule, Depends(MailingListModule)],
    _=Depends(authorized(["groups"], PermissionTier.manager)),
) -> None:
    """Manager kick a member from a mailing list by email"""
    try:
        module.kick_member(mailing_list_id, email)
    except MemberNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
