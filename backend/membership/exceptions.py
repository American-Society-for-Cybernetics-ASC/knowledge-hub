class MembershipError(Exception):
    """Raised when an error occurs within the Membership Module."""


class NotApprovedError(MembershipError):
    """Raised when the given user has not been approved for membership"""


class AlreadyAMemberError(MembershipError):
    """Raised when the given user is already a member"""


class NotAMemberError(MembershipError):
    """Raised when the given user isn't a member"""


class MembershipTypeNotFoundError(MembershipError):
    """Raised when a membership type doesn't exist"""


class MembershipTypeOutOfDateError(MembershipError):
    """Raised when a membership type is no longer valid"""
