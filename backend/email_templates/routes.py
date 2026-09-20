from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from auth_module import PermissionTier, authorized
from email_templates.module import EmailTemplatesModule
from email_templates.model import EmailTemplateData, EmailTemplateUpdate

email_templates_router = APIRouter(prefix="/email-templates", tags=["email-templates"])


@email_templates_router.get("")
def get_templates(
    module: Annotated[EmailTemplatesModule, Depends(EmailTemplatesModule)],
    _=Depends(authorized(["email_templates"], PermissionTier.manager)),
) -> list[EmailTemplateData]:
    """Get all email templates."""
    return module.get_templates()


@email_templates_router.get("/{name}")
def get_template(
    name: str,
    module: Annotated[EmailTemplatesModule, Depends(EmailTemplatesModule)],
    _=Depends(authorized(["email_templates"], PermissionTier.manager)),
) -> EmailTemplateData:
    """Get a specific email template by name."""
    template = module.get_template(name)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@email_templates_router.patch("/{name}")
def update_template(
    name: str,
    update: EmailTemplateUpdate,
    module: Annotated[EmailTemplatesModule, Depends(EmailTemplatesModule)],
    _=Depends(authorized(["email_templates"], PermissionTier.manager)),
) -> EmailTemplateData:
    """Update an email template."""
    template = module.update_template(name, update)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
