from enum import Enum
from typing import Callable

from fastapi import HTTPException, Request

from utils import BaseModel
from settings import SETTINGS
from .module import AuthModule as AuthModule


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


class Permission(BaseModel):
    """Note that these do not have a total ordering: there are some permissions where neither is greater than the other"""

    heirarchy: list[str]
    tier: PermissionTier

    def includes(self, other: Permission) -> bool:
        return (
            self.tier >= other.tier
            and len(self.heirarchy) <= len(other.heirarchy)
            and self.heirarchy == other.heirarchy[: len(self.heirarchy)]
        )


def authorized(heirarchy: list[str], tier: PermissionTier) -> Callable:
    """Check that the caller has the given permission"""
    permission = Permission(heirarchy=heirarchy, tier=tier)

    def inner(request: Request):
        _authorization = request.get("authorization")

        if SETTINGS.local_deployment:
            user_permissions = [
                Permission(heirarchy=[], tier=PermissionTier.adminstrator)
            ]
        else:
            # TODO: don't default to admin on prod
            user_permissions = [
                Permission(heirarchy=[], tier=PermissionTier.adminstrator)
            ]

        if not any((p.includes(permission) for p in user_permissions)):
            raise HTTPException(401, "Unauthorized")

    return inner
