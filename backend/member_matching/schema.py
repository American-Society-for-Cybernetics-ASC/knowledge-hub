from utils import BaseModel


class MemberMatchingSuggestion(BaseModel):
    """Member suggestion."""

    member_id: int
    display_name: str | None
    shared_tags: list[str]
    score: int


class MemberMatchSuggestionsResult(BaseModel):
    """Suggestions available to member."""

    opted_out: bool
    suggestions: list[MemberMatchingSuggestion]


class MatchingPreferenceResult(BaseModel):
    """Current matching preference."""

    matching_opt_out: bool


class DismissMatchRequest(BaseModel):
    """Request to hide one suggested member."""

    suggested_member_id: int


class DismissMatchResult(BaseModel):
    """Confirmation of match dismissal."""

    suggested_member_id: int
