from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from auth_module.model import PermissionTier, Permissions
from member_application.model import MembershipApplication
from utils import BaseModel
from database.types import ApplicationStatus, PermissionCategory
from member_application.module import (
    ApplicationCompleteError,
    MemberApplicationModule,
    ApplicationNotFoundError,
    ApplicationNotOwnedError,
)
from auth_module import authorized, permissions, user_id

member_application_router = APIRouter(
    prefix="/membership/application", tags=["membership", "application"]
)


class ReadMembershipApplication(BaseModel):
    application_id: int
    user_id: int
    member_type: str | None
    status: ApplicationStatus
    submitted_at: datetime
    last_edited: datetime
    content: str

    @staticmethod
    def from_model(
        model: MembershipApplication,
    ) -> ReadMembershipApplication:
        return ReadMembershipApplication(
            application_id=model.application_id,
            user_id=model.user_id,
            member_type=model.member_type.name
            if model.member_type is not None
            else None,
            status=model.status,
            submitted_at=model.submitted_at,
            last_edited=model.last_edited,
            content=model.content,
        )


@member_application_router.get("")
def get_applications(
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
    user_id: Annotated[int, Depends(user_id)],
) -> list[ReadMembershipApplication]:
    """get a list of all of your member applications"""
    return list(
        map(
            ReadMembershipApplication.from_model,
            module.get_users_applications(user_id),
        )
    )


class SubmitApplication(BaseModel):
    member_type_id: UUID
    content: str


@member_application_router.post("")
def submit_application(
    application: SubmitApplication,
    user_id: Annotated[int, Depends(user_id)],
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
) -> ReadMembershipApplication:
    """submit a new application"""

    if user_id is None:
        raise HTTPException(status_code=401, detail="authentication required")

    return ReadMembershipApplication.from_model(
        module.submit_application(
            user_id, application.content, application.member_type_id
        )
    )


class ReviseApplication(BaseModel):
    content: str


@member_application_router.patch("/{application_id}")
def revise_application(
    application_id: int,
    application: ReviseApplication,
    user_id: Annotated[int, Depends(user_id)],
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
) -> ReadMembershipApplication:
    """revise an existing application"""

    if user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        return ReadMembershipApplication.from_model(
            module.revise_application(application_id, user_id, application.content)
        )
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ApplicationNotOwnedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ApplicationCompleteError as e:
        raise HTTPException(status_code=400, detail=str(e))


@member_application_router.get("/{application_id}")
def get_application(
    application_id: int,
    user_id: Annotated[int, Depends(user_id)],
    permissions: Annotated[Permissions, Depends(permissions)],
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
) -> ReadMembershipApplication:
    """get a single member application"""
    try:
        application = module.get_application(application_id)
        if application.user_id != user_id:
            # Moderator permission required to view other's applications
            if not permissions.includes(
                [PermissionCategory.MEMBERSHIP], PermissionTier.moderator
            ):
                raise ApplicationNotFoundError()
        return ReadMembershipApplication.from_model(application)
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@member_application_router.post("/{application_id}/approve")
def approve_application(
    application_id: int,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> ReadMembershipApplication:
    """approve a member application"""
    try:
        return ReadMembershipApplication.from_model(
            module.approve_application(application_id)
        )
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@member_application_router.post("/{application_id}/deny")
def deny_application(
    application_id: int,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> ReadMembershipApplication:
    """deny a member application"""
    try:
        return ReadMembershipApplication.from_model(
            module.deny_application(application_id)
        )
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@member_application_router.post("/{application_id}/request-revision")
def request_revision(
    application_id: int,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> ReadMembershipApplication:
    """ "requets a revision for an application"""
    try:
        return ReadMembershipApplication.from_model(
            module.request_revision(application_id)
        )
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@member_application_router.get("/admin/all")
def get_all_applications(
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)],
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> list[ReadMembershipApplication]:
    """get a list of all member applications"""
    return list(
        map(ReadMembershipApplication.from_model, module.get_all_applications())
    )
