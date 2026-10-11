from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from auth_module.model import PermissionTier, Permissions
import database
from database.model import AuthUser, MembershipApplication
from utils import BaseModel
from database.types import ApplicationStatus, PermissionCategory
from member_application.application_module import (
    ApplicationCompleteError,
    ApplicationNotFoundError,
    ApplicationNotOwnedError,
)
from auth_module import authorized, permissions, user_id
from . import application_module

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
    def from_db_model(
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


class ApplicationSummary(BaseModel):
    user_id: int
    email: str
    name: str
    last_application: datetime


@member_application_router.get("")
def get_applications(
    user_id: Annotated[int, Depends(user_id)],
) -> list[ReadMembershipApplication]:
    """get a list of all of your member applications"""
    with database.get_session() as session:
        return list(
            map(
                ReadMembershipApplication.from_db_model,
                application_module.get_users_applications(session, user_id),
            )
        )


class SubmitApplication(BaseModel):
    member_type_id: UUID
    content: str


@member_application_router.post("")
def submit_application(
    application: SubmitApplication,
    user_id: Annotated[int, Depends(user_id)],
) -> ReadMembershipApplication:
    """submit a new application"""

    if user_id is None:
        raise HTTPException(status_code=401, detail="authentication required")

    with database.with_transaction() as session:
        return ReadMembershipApplication.from_db_model(
            application_module.submit_application(
                session, user_id, application.content, application.member_type_id
            )
        )


class ReviseApplication(BaseModel):
    content: str


@member_application_router.patch("/{application_id}")
def revise_application(
    application_id: int,
    application: ReviseApplication,
    user_id: Annotated[int, Depends(user_id)],
) -> ReadMembershipApplication:
    """revise an existing application"""

    if user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        with database.with_transaction() as session:
            return ReadMembershipApplication.from_db_model(
                application_module.revise_application(
                    session, application_id, user_id, application.content
                )
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
) -> ReadMembershipApplication:
    """get a single member application"""
    with database.get_session() as session:
        try:
            application = application_module.get_application(session, application_id)
            if application.user_id != user_id:
                # Moderator permission required to view other's applications
                if not permissions.includes(
                    [PermissionCategory.MEMBERSHIP], PermissionTier.moderator
                ):
                    raise ApplicationNotFoundError()
            return ReadMembershipApplication.from_db_model(application)
        except ApplicationNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))


@member_application_router.post("/{application_id}/approve")
def approve_application(
    application_id: int,
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> ReadMembershipApplication:
    """approve a member application"""
    try:
        with database.with_transaction() as session:
            return ReadMembershipApplication.from_db_model(
                application_module.approve_application(session, application_id)
            )
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@member_application_router.post("/{application_id}/deny")
def deny_application(
    application_id: int,
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> ReadMembershipApplication:
    """deny a member application"""
    try:
        with database.with_transaction() as session:
            return ReadMembershipApplication.from_db_model(
                application_module.deny_application(session, application_id)
            )
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@member_application_router.post("/{application_id}/request-revision")
def request_revision(
    application_id: int,
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> ReadMembershipApplication:
    """ "requets a revision for an application"""
    try:
        with database.with_transaction() as session:
            return ReadMembershipApplication.from_db_model(
                application_module.request_revision(session, application_id)
            )
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@member_application_router.get("/admin/all")
def get_all_applications(
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> list[ReadMembershipApplication]:
    """get a list of all member applications"""
    with database.get_session() as session:
        return list(
            map(
                ReadMembershipApplication.from_db_model,
                application_module.get_all_applications(session),
            )
        )


@member_application_router.get("/admin/summary")
def get_applications_summary(
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> list[ApplicationSummary]:
    """get a list of all member applications"""
    with database.get_session() as session:
        return [
            ApplicationSummary(
                user_id=user.user_id,
                email=user.email,
                name=user.name or user.email,
                last_application=max(map(lambda x: x.last_edited, user.applications)),
            )
            for user in session.query(AuthUser).join(
                AuthUser.applications.and_(
                    MembershipApplication.status == ApplicationStatus.PENDING
                )
            )
        ]


@member_application_router.get("/admin/all/{user_id}")
def get_users_applications(
    user_id: int,
    _=Depends(authorized([PermissionCategory.MEMBERSHIP], PermissionTier.manager)),
) -> list[ReadMembershipApplication]:
    """get a list of all member applications"""
    with database.get_session() as session:
        return list(
            map(
                ReadMembershipApplication.from_db_model,
                application_module.get_users_applications(session, user_id),
            )
        )
