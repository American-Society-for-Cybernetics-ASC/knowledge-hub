from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from member_application.module import MemberApplicationModule, ApplicationNotFoundError
from member_application.model import MemberApplication, SubmitApplication, ReviseApplication

member_application_router = APIRouter(prefix="/member-applications", tags=["member-applications"])

@member_application_router.get("/")
def get_applications(
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)]
) -> list[MemberApplication]:
    """get a list of all member applications"""
    return module.get_applications()

@member_application_router.get("/{application_id}")
def get_application(
    application_id: int,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)]
) -> MemberApplication:
    """get a single member application"""
    try:
        return module.get_application(application_id)
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@member_application_router.post("/")
def submit_application(
    application: SubmitApplication,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)]
) -> MemberApplication:
    """submit a new application"""
    return module.submit_application(
        application.member_id,
        application.content
    )

@member_application_router.patch("/{application_id}")
def revise_application(
    application_id: int,
    application: ReviseApplication,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)]
) -> MemberApplication:
    """revise an existing application"""
    try:
        return module.revise_application(application_id, application.content)
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@member_application_router.post("/{application_id}/approve")
def approve_application(
    application_id: int,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)]
) -> MemberApplication:
    """approve a member application"""
    try:
        return module.approve_application(application_id)
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@member_application_router.post("/{application_id}/deny")
def deny_application(
    application_id: int,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)]
) -> MemberApplication:
    """deny a member application"""
    try:
        return module.deny_application(application_id)
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@member_application_router.post("/{application_id}/request-revision")
def request_revision(
    application_id: int,
    module: Annotated[MemberApplicationModule, Depends(MemberApplicationModule)]
) -> MemberApplication:
    """"requets a revision for an application"""
    try:
        return module.request_revision(application_id)
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

