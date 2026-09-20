from typing import Annotated, Callable

from fastapi import Depends, HTTPException, Request

from auth_module.model import Permissions, PermissionTier

from .module import AuthModule as AuthModule
from jose import jwt

import database
from database import model


def user_id(request: Request) -> int | None:
    """
    Extract the user's id.

    ```python
    @app.get("")
    def my_route(user_id: Annotated[int | None, Depends(user_id)]):
        ...
    ```
    """
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
    if user_id is None:
        return Permissions()

    with database.get_session() as session:
        user = session.get(model.AuthUser, user_id)

    if not user or not user.permissions:
        return Permissions()

    return Permissions.model_validate(user.permissions)


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
