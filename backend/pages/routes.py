from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
import database
from database import model
from utils import BaseModel
from auth_module import authorized
from auth_module.model import PermissionTier

pages_router = APIRouter(prefix="/pages", tags=["pages"])


class PageContent(BaseModel):
    content: str


@pages_router.get("/{slug}")
def get_page(slug: str) -> PageContent:
    """Get the content of a static page by slug."""
    with database.get_session() as session:
        page = session.get(model.StaticPage, slug)
        if not page:
            return PageContent(content="")
        return PageContent(content=page.content)


@pages_router.put("/{slug}")
def update_page(
    slug: str,
    req: PageContent,
    _=Depends(authorized(["auth"], PermissionTier.manager)),
) -> PageContent:
    """Update the content of a static page. Requires manager or above."""
    with database.get_session() as session:
        page = session.get(model.StaticPage, slug)
        if not page:
            page = model.StaticPage(slug=slug, content=req.content)
            session.add(page)
        else:
            page.content = req.content
        session.commit()
        return PageContent(content=req.content)