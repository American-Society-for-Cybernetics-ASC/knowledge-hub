from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

import database
from database import model
from utils import BaseModel
from auth_module import authorized
from auth_module.model import PermissionTier
from notifications import NotificationsModule
from notifications.module import NotificationData

newsletter_router = APIRouter(prefix="/newsletters", tags=["newsletters"])


class NewsletterResponse(BaseModel):
    id: int
    name: str
    content: str
    published: bool
    published_at: datetime | None
    created_at: datetime | None


class NewsletterCreate(BaseModel):
    name: str
    content: str = ""


class NewsletterUpdate(BaseModel):
    name: str
    content: str


@newsletter_router.get("/")
def list_newsletter() -> list[NewsletterResponse]:
    with database.get_session() as session:
        newsletters = session.scalars(
            select(model.Newsletter)
            .where(model.Newsletter.published)
            .order_by(model.Newsletter.published_at.desc())
        ).all()
        return [NewsletterResponse.model_validate_sqlalchemy(n) for n in newsletters]


@newsletter_router.get("/all")
def list_all_newsletters(
    _=Depends(authorized(["auth"], PermissionTier.manager)),
) -> list[NewsletterResponse]:
    with database.get_session() as session:
        newsletters = session.scalars(
            select(model.Newsletter).order_by(model.Newsletter.created_at.desc())
        ).all()
        return [NewsletterResponse.model_validate_sqlalchemy(n) for n in newsletters]


@newsletter_router.post("/")
def create_newsletter(
    req: NewsletterCreate,
    _=Depends(authorized(["auth"], PermissionTier.manager)),
) -> NewsletterResponse:
    with database.get_session() as session:
        newsletter = model.Newsletter(name=req.name, content=req.content)
        session.add(newsletter)
        session.commit()
        session.refresh(newsletter)
        return NewsletterResponse.model_validate_sqlalchemy(newsletter)


@newsletter_router.put("/{newsletter_id}")
def update_newsletter(
    newsletter_id: int,
    req: NewsletterUpdate,
    _=Depends(authorized(["auth"], PermissionTier.manager)),
) -> NewsletterResponse:
    with database.get_session() as session:
        newsletter = session.get(model.Newsletter, newsletter_id)
        if not newsletter:
            raise HTTPException(status_code=404, detail="Newsletter not found")
        newsletter.name = req.name
        newsletter.content = req.content
        session.commit()
        session.refresh(newsletter)
        return NewsletterResponse.model_validate_sqlalchemy(newsletter)


@newsletter_router.post("/{newsletter_id}/publish")
def publish_newsletter(
    newsletter_id: int,
    _=Depends(authorized(["auth"], PermissionTier.manager)),
) -> NewsletterResponse:
    with database.get_session() as session:
        newsletter = session.get(model.Newsletter, newsletter_id)
        if not newsletter:
            raise HTTPException(status_code=404, detail="Newsletter not found")
        if newsletter.published:
            raise HTTPException(status_code=400, detail="Already published")

        newsletter.published = True
        newsletter.published_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(newsletter)

        # Notify all users
        users = session.scalars(select(model.AuthUser)).all()
        for user in users:
            NotificationsModule().create_notification(
                NotificationData(
                    user_id=user.user_id,
                    subject=f"New Newsletter: {newsletter.name}",
                    message=f"A new newsletter has been published: {newsletter.name}. Read it at /newsletters/{newsletter_id}",
                ),
                email_provider=None,  # TODO
            )

        return NewsletterResponse.model_validate_sqlalchemy(newsletter)
