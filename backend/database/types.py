from enum import Enum


class MemberStatus(str, Enum):
    CURRENT = "Current"
    EXPIRED = "Expired"
