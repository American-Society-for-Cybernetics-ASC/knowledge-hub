from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from .module import MailingListModule, MemberNotFoundError, MailingListNotFoundError
from google.auth.exceptions import GoogleAuthError
from .model import MailingList, MailingListMember
from mailing_list.providers.google_workspace_provider import (
    GoogleWorkspaceConfigurationError,
)
from auth_module import authorized, user_id, PermissionTier


mailing_list_router = APIRouter(prefix="/mailing-lists", tags=["mailing-lists"])


def get_mailing_list_module() -> MailingListModule:
    return MailingListModule()


@mailing_list_router.get("/")
def get_mailing_lists(
    module: Annotated[MailingListModule, Depends(get_mailing_list_module)],
) -> list[MailingList]:
    return module.get_mailing_lists()


@mailing_list_router.post("/register")
def register_mailing_list(
    mailing_list_email: str,
    module: Annotated[MailingListModule, Depends(get_mailing_list_module)],
    _=Depends(authorized(["groups"], PermissionTier.manager)),
) -> MailingList:
    """Manager register an existing Google Workspace Group"""
    return module.register_mailing_list(mailing_list_email)


@mailing_list_router.post("/{mailing_list_id}/join")
def join_mailing_list(
    mailing_list_id: int,
    member_id: Annotated[int, Depends(user_id)],
    module: Annotated[MailingListModule, Depends(get_mailing_list_module)],
) -> None:
    """join a mailing list"""
    try:
        module.join_mailing_list(mailing_list_id, member_id)
    except (MemberNotFoundError, MailingListNotFoundError) as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e
    except (GoogleWorkspaceConfigurationError, GoogleAuthError) as e:
        raise HTTPException(
            status_code=503,
            detail="unable to update Google workspace mailing list",
        ) from e


@mailing_list_router.get("/{mailing_list_id}/members")
def get_mailing_list_members(
    mailing_list_id: int,
    module: Annotated[MailingListModule, Depends(get_mailing_list_module)],
) -> list[MailingListMember]:
    """get a list of all members from a mailing list"""
    return module.get_mailing_list_members(mailing_list_id)


@mailing_list_router.post("/{mailing_list_id}/members/add")
def add_member(
    mailing_list_id: int,
    email: str,
    module: Annotated[MailingListModule, Depends(get_mailing_list_module)],
    _=Depends(authorized(["groups"], PermissionTier.manager)),
) -> None:
    """Manager add a member to a group by email"""
    try:
        module.add_member(mailing_list_id, email)
    except (MemberNotFoundError, MailingListNotFoundError) as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e

    except (GoogleWorkspaceConfigurationError, GoogleAuthError) as e:
        raise HTTPException(
            status_code=503,
            detail="unable to update Google workspace mailing list",
        ) from e


@mailing_list_router.post("/{mailing_list_id}/leave")
def leave_mailing_list(
    mailing_list_id: int,
    member_id: Annotated[int, Depends(user_id)],
    module: Annotated[MailingListModule, Depends(get_mailing_list_module)],
) -> None:
    """leave a mailing list"""
    try:
        module.leave_mailing_list(mailing_list_id, member_id)
    except (MemberNotFoundError, MailingListNotFoundError) as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e

    except (GoogleWorkspaceConfigurationError, GoogleAuthError) as e:
        raise HTTPException(
            status_code=503,
            detail="unable to update Google workspace mailing list",
        ) from e


@mailing_list_router.post("/{mailing_list_id}/members/kick")
def kick_member(
    mailing_list_id: int,
    email: str,
    module: Annotated[MailingListModule, Depends(get_mailing_list_module)],
    _=Depends(authorized(["groups"], PermissionTier.manager)),
) -> None:
    """Manager kick a member from a mailing list by email"""
    try:
        module.kick_member(mailing_list_id, email)
    except (MemberNotFoundError, MailingListNotFoundError) as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        ) from e
    except (GoogleWorkspaceConfigurationError, GoogleAuthError) as e:
        raise HTTPException(
            status_code=503,
            detail="unable to update Google workspace mailing list",
        ) from e
