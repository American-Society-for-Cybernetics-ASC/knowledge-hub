from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from . import NotificationsModule

notifications_router = APIRouter(prefix="/notifications")


# Request schemas

class SendAllMembersRequest(BaseModel):
    subject: str
    content: str


class ApplicationStatusRequest(BaseModel):
    email: str
    name: str


class RevisionRequestedRequest(BaseModel):
    email: str
    name: str
    notes: str


class MembershipStatusRequest(BaseModel):
    email: str
    name: str
    status: str


# Endpoints

@notifications_router.post("/send-all-members")
def send_email_to_all_members(
    req: SendAllMembersRequest,
    module: Annotated[NotificationsModule, Depends(NotificationsModule)],
) -> dict:
    """
    Sends an email to all members.
    """
    try:
        module.send_email_to_all_members(
            subject=req.subject,
            content=req.content
        )
        return {"message": "Email sent to all members successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@notifications_router.post("/notify-managers-new-application")
def notify_managers_new_application(
    req: ApplicationStatusRequest,
    module: Annotated[NotificationsModule, Depends(NotificationsModule)],
) -> dict:
    """
    Notifies all managers that a new membership application has been submitted.
    """
    try:
        module.notify_managers_new_application(
            applicant_email=req.email,
            applicant_name=req.name
        )
        return {"message": "Managers notified successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@notifications_router.post("/notify-applicant-approved")
def notify_applicant_approved(
    req: ApplicationStatusRequest,
    module: Annotated[NotificationsModule, Depends(NotificationsModule)],
) -> dict:
    """
    Notifies an applicant that their application has been approved.
    """
    try:
        module.notify_applicant_approved(
            email=req.email,
            name=req.name
        )
        return {"message": "Applicant notified of approval."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@notifications_router.post("/notify-applicant-denied")
def notify_applicant_denied(
    req: ApplicationStatusRequest,
    module: Annotated[NotificationsModule, Depends(NotificationsModule)],
) -> dict:
    """
    Notifies an applicant that their application has been denied.
    """
    try:
        module.notify_applicant_denied(
            email=req.email,
            name=req.name
        )
        return {"message": "Applicant notified of denial."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@notifications_router.post("/notify-applicant-revision")
def notify_applicant_revision_requested(
    req: RevisionRequestedRequest,
    module: Annotated[NotificationsModule, Depends(NotificationsModule)],
) -> dict:
    """
    Notifies an applicant that a revision has been requested.
    """
    try:
        module.notify_applicant_revision_requested(
            email=req.email,
            name=req.name,
            notes=req.notes
        )
        return {"message": "Applicant notified of revision request."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@notifications_router.post("/notify-membership-status")
def notify_membership_status(
    req: MembershipStatusRequest,
    module: Annotated[NotificationsModule, Depends(NotificationsModule)],
) -> dict:
    """
    Sends a membership status notification to a member.
    """
    try:
        module.notify_membership_status(
            email=req.email,
            name=req.name,
            status=req.status
        )
        return {"message": "Membership status notification sent."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))