from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from auth_module.model import PermissionTier, Permissions
from database.types import PermissionCategory
from member_application.module import (
    MemberApplicationModule,
    ApplicationNotFoundError,
    ApplicationNotOwnedError,
)
from member_application.model import (
    MemberApplication,
    SubmitApplication,
    ReviseApplication,
)
from auth_module import authorized, permissions, user_id

member_application_router = APIRouter(
    prefix="/member-applications", tags=["member-applications"]
)


@member_application_router.get("/")
def get_applications(
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> list[MemberApplication]:
    """get a list of all member applications"""
    return module.get_applications()


@member_application_router.get("/{application_id}")
def get_application(
    application_id: int,
    user_id: Annotated[int, Depends(user_id)],
    permissions: Annotated[Permissions, Depends(permissions)],
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
) -> MemberApplication:
    """get a single member application"""
    try:
        application = module.get_application(application_id)
        if application.auth_user_id != user_id:
            # Moderator permission required to view other's applications
            if not permissions.includes(
                [PermissionCategory.MEMBERSHIP], PermissionTier.moderator
            ):
                raise ApplicationNotFoundError()
        return application
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@member_application_router.post("/")
def submit_application(
    application: SubmitApplication,
    auth_user_id: Annotated[int, Depends(user_id)],
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
) -> MemberApplication:
    """submit a new application"""

    if auth_user_id is None:
        raise HTTPException(status_code=401, detail="authentication required")

    return module.submit_application(
        auth_user_id,
        application.content,
    )


@member_application_router.patch("/{application_id}")
def revise_application(
    application_id: int,
    application: ReviseApplication,
    auth_user_id: Annotated[int, Depends(user_id)],
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
) -> MemberApplication:
    """revise an existing application"""

    if auth_user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        return module.revise_application(
            application_id, auth_user_id, application.content
        )
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ApplicationNotOwnedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@member_application_router.post("/{application_id}/approve")
def approve_application(
    application_id: int,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> MemberApplication:
    """approve a member application"""
    try:
        return module.approve_application(application_id)
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@member_application_router.post("/{application_id}/deny")
def deny_application(
    application_id: int,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> MemberApplication:
    """deny a member application"""
    try:
        return module.deny_application(application_id)
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@member_application_router.post("/{application_id}/request-revision")
def request_revision(
    application_id: int,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> MemberApplication:
    """ "requets a revision for an application"""
    try:
        return module.request_revision(application_id)
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
