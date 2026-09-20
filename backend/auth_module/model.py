from utils import BaseModel
from enum import Enum
from typing import Optional
from database import model as dbmodel


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
        if self.tier and self.tier >= tier:
            return True

        if len(heirarchy) == 0:
            return False

        next = self.children.get(heirarchy[0])
        if next:
            return next.includes(heirarchy[1:], tier)

        return False
