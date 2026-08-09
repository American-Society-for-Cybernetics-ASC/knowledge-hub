from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from .module import GroupModule, MemberNotFoundError
from .model import Group, GroupMember
from auth_module import authorized, user_id, PermissionTier

groups_router = APIRouter(prefix="/groups", tags=["groups"])

@groups_router.get("/")
def get_groups(
    module: Annotated[GroupModule, Depends(GroupModule)],
) -> list[Group]:
    return module.get_groups()

@groups_router.post("/register")
def register_group(
    mailing_list_email: str,
    module: Annotated[GroupModule, Depends(GroupModule)],
    _=Depends(authorized(["groups"], PermissionTier.manager)),
) -> Group:
    """Manager register an existing Google Workspace Group"""
    try:
        return module.register_group(mailing_list_email)
    except Exception as e:
        raise HTTPException(
            status_code=409,
            detail=f"Group {mailing_list_email} already exists",
        )

@groups_router.post("/{group_id}/join")
def join_group(
    group_id: int,
    member_id: Annotated[int, Depends(user_id)],
    module: Annotated[GroupModule, Depends(GroupModule)],
) -> None:
    """join a group"""
    try:
        module.join_group(group_id, member_id)
    except MemberNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@groups_router.get("/{group_id}/members")
def get_group_members(
    group_id: int,
    module: Annotated[GroupModule, Depends(GroupModule)],
) -> list[GroupMember]:
        """get a list of all members from a group"""
        return module.get_group_members(group_id)

@groups_router.post("/{group_id}/members/add")
def add_member(
    group_id: int,
    email: str, 
    module: Annotated[GroupModule, Depends(GroupModule)],
    _=Depends(authorized(["groups"], PermissionTier.manager)),
) -> None:
    """Manager add a member to a group by email"""
    try:
        module.add_member(group_id, email)
    except MemberNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

@groups_router.post("/{group_id}/leave")
def leave_group(
    group_id: int,
    member_id: Annotated[int, Depends(user_id)],
    module: Annotated[GroupModule, Depends(GroupModule)],
) -> None:
    """leave a group"""
    try:
        module.leave_group(group_id, member_id)
    except MemberNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

@groups_router.post("/{group_id}/members/kick")
def kick_member(
    group_id: int,
    email: str,
    module: Annotated[GroupModule, Depends(GroupModule)],
    _=Depends(authorized(["groups"], PermissionTier.manager)),
) -> None:
    """Manager kick a member from a group by email"""
    try:
        module.kick_member(group_id, email)
    except MemberNotFoundError as e:
         raise HTTPException(
              status_code=404,
              detail=str(e),
         )