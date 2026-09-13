from typing import Annotated

from fastapi import APIRouter, Depends

from members.routes import get_current_member_id

from .module import MemberMatchingModule
from .schema import (
    DismissMatchRequest,
    DismissMatchResult,
    MemberMatchSuggestionsResult,
    MatchingPreferenceResult,
)


member_matching_router = APIRouter(
    prefix="/member-matching",
    tags=["Member Matching"],
)


@member_matching_router.get(
    "",
    response_model=MemberMatchSuggestionsResult,
)
def get_suggestions(
    member_id: Annotated[int, Depends(get_current_member_id)],
    module: Annotated[MemberMatchingModule, Depends(MemberMatchingModule)],
) -> MemberMatchSuggestionsResult:
    """Return tag based suggestions for a member."""
    return module.get_suggestions(member_id)


@member_matching_router.post(
    "/dismiss",
    response_model=DismissMatchResult,
)
def dismiss_suggestion(
    request: DismissMatchRequest,
    member_id: Annotated[int, Depends(get_current_member_id)],
    module: Annotated[MemberMatchingModule, Depends(MemberMatchingModule)],
) -> DismissMatchResult:
    """Hide one suggestion for dismissal period."""
    return module.dismiss_suggestion(
        member_id=member_id,
        suggested_member_id=request.suggested_member_id,
    )


@member_matching_router.post(
    "/opt-out",
    response_model=MatchingPreferenceResult,
)
def opt_out(
    member_id: Annotated[int, Depends(get_current_member_id)],
    module: Annotated[MemberMatchingModule, Depends(MemberMatchingModule)],
) -> MatchingPreferenceResult:
    """Disable matching for a member."""
    return module.set_opt_out(
        member_id=member_id,
        matching_opt_out=True,
    )


@member_matching_router.post(
    "/opt-in",
    response_model=MatchingPreferenceResult,
)
def opt_in(
    member_id: Annotated[int, Depends(get_current_member_id)],
    module: Annotated[MemberMatchingModule, Depends(MemberMatchingModule)],
) -> MatchingPreferenceResult:
    """Enable matching for a member."""
    return module.set_opt_out(
        member_id=member_id,
        matching_opt_out=False,
    )
