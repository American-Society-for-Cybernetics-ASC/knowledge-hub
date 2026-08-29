from enum import Enum
from typing import Annotated, Callable, Optional

from fastapi import Depends, HTTPException, Request

from utils import BaseModel
from settings import SETTINGS
from .module import AuthModule as AuthModule
from jose import jwt

import database
from database import model


class PermissionTier(Enum):
    moderator = "moderator"
    manager = "manager"
    adminstrator = "administrator"

    def __eq__(self, other):
        if isinstance(other, PermissionTier):
            return self._member_names_.index(self.name) == self._member_names_.index(
                other.name
            )
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, PermissionTier):
            return self._member_names_.index(self.name) > self._member_names_.index(
                other.name
            )
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, PermissionTier):
            return self._member_names_.index(self.name) >= self._member_names_.index(
                other.name
            )
        return NotImplemented


class Permissions(BaseModel):
    """A User's permissions, structured as a tree"""

    tier: Optional[PermissionTier] = None
    """Optional for e.g. a normal member with no permissions, who was made moderator of a single repository"""

    children: dict[str, Permissions] = {}

    def includes(self, heirarchy: list[str], tier: PermissionTier) -> bool:
        if self.tier and self.tier > tier:
            return True

        if len(heirarchy) == 0:
            return False

        next = self.children.get(heirarchy[0])
        if next:
            return next.includes(heirarchy[1:], tier)

        return False


def user_id(request: Request) -> int | None:
    """
    Extract the user's id.

    ```python
    @app.get("")
    def my_route(user_id: Annotated[int, Depends(user_id)]):
        ...
    ```
    """
    if SETTINGS.testing:
        return 0

    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        public_key_pem = AuthModule()._get_public_key_pem()
        payload = jwt.decode(token, public_key_pem, algorithms=["RS256"])
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def permissions(user_id: Annotated[int | None, Depends(user_id)]) -> Permissions:
    """
    Extracts the user's permissions.

    ```python
    @app.get("")
    def my_route(permissions: Annotated[Permissions, Depends(permissions)]):
        ...
    ```
    """
    if SETTINGS.testing:
        return Permissions(tier=PermissionTier.adminstrator, children={})

    if user_id is None:
        return Permissions()

    session = database.get_session()
    user = session.get(model.AuthUser, user_id)

    if not user or not user.permissions:
        return Permissions()

    return Permissions.model_validate_sqlalchemy(user.permissions)


def authorized(heirarchy: list[str], tier: PermissionTier) -> Callable:
    """
    Check that the caller has the given permission.

    Usage example:
    ```python
    @app.get("")
    def my_route(_ = Depends(authorized(["module", "subpermission"], PermissionTier.manager))):
        ...
    ```
    """

    def inner(permissions: Annotated[Permissions, Depends(permissions)]):
        if not permissions.includes(heirarchy, tier):
            raise HTTPException(401, "Unauthorized")

    return inner
