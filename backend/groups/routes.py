from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from .module import GroupModule, MemberNotFoundError
from .model import Group, GroupMember

groups_router = APIRouter(prefix="/groups", tags=["groups"])

@groups_router.get("/")
def get_groups(
    module: Annotated[GroupModule, Depends(GroupModule)],
) -> list[Group]:
    return module.get_groups()

@groups_router.post("/register")
def register_group(
    mailing_list_email: str,
    manager_id: int,
    module: Annotated[GroupModule, Depends(GroupModule)],
) -> Group:
    try:
        return module.register_group(mailing_list_email, manager_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@groups_router.post("/{group_id}/join")
def join_group(
    group_id: int,
    member_id: int,
    module: Annotated[GroupModule, Depends(GroupModule)],
) -> None:
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
        return module.get_group_members(group_id)

@groups_router.post("/{group_id}/members/{member_id}/add")
def add_member(
    group_id: int,
    member_id: int, 
    manager_id: int,
    module: Annotated[GroupModule, Depends(GroupModule)],
) -> None:
    try:
        module.add_member(group_id, member_id, manager_id)
    except MemberNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

@groups_router.post("/{group_id}/leave")
def leave_group(
    group_id: int,
    member_id: int,
    module: Annotated[GroupModule, Depends(GroupModule)],
) -> None:
    try:
        module.leave_group(group_id, member_id)
    except MemberNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

@groups_router.post("/{group_id}/members/{member_id}/kick")
def kick_member(
    group_id: int,
    member_id: int,
    module: Annotated[GroupModule, Depends(GroupModule)],
) -> None:
    try:
            module.kick_member(group_id, member_id)
    except MemberNotFoundError as e:
         raise HTTPException(
              status_code=404,
              detail=str(e),
         )