from datetime import datetime, timedelta, timezone
from typing import Callable

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database import model
from main import app
from member_matching.module import MemberMatchingModule
from members.routes import get_current_member_id


def create_member(
    get_session: Callable[[], Session],
    email: str,
    *,
    tags: list[str] | None = None,
    display_name: str | None = None,
    matching_opt_out: bool = False,
    has_current_membership: bool = True,
) -> int:
    """Create a member with a profile and current membership."""
    with get_session() as session:
        auth_user = model.AuthUser(email=email)
        session.add(auth_user)
        session.flush()

        member = model.Member(
            auth_user_id=auth_user.user_id,
            due_date=datetime.now(timezone.utc)
            + (timedelta(10) if has_current_membership else timedelta(-10)),
            member_type_id=None,
        )
        session.add(member)
        session.flush()

        session.add(
            model.Profile(
                member_id=member.auth_user_id,
                tags=tags or [],
                content={
                    "identity": {
                        "display_name": display_name,
                    }
                },
                matching_opt_out=matching_opt_out,
            )
        )

        session.commit()
        return member.auth_user_id


@pytest.fixture
def authenticate_member():
    """
    Test matching behaviour rather than JWT authentication.

    Override the dependency to get the current member ID.
    """

    def set_authenticated_member(member_id: int) -> None:
        # Override the dependency to get the current member ID
        app.dependency_overrides[get_current_member_id] = lambda: member_id

    yield set_authenticated_member

    # Clean up the override
    app.dependency_overrides.pop(get_current_member_id, None)


def test_suggestions_rank_members_by_tags(mock_get_session):
    """Suggestions use shared tags, exclude self."""
    active_member_id = create_member(
        mock_get_session,
        email="a",
        tags=[" AI ", "Python", "ai"],
        display_name="Active Member",
    )
    one_shared_tag_member_id = create_member(
        mock_get_session,
        email="b",
        tags=["python"],
        display_name="One Shared Tag",
    )
    two_shared_tags_member_id = create_member(
        mock_get_session,
        email="c",
        tags=["AI", "PYTHON"],
        display_name="Two Shared Tags",
    )
    create_member(
        mock_get_session,
        email="d",
        tags=["AI"],
        display_name="No Current Membership",
        has_current_membership=False,
    )

    result = MemberMatchingModule().get_suggestions(active_member_id)

    assert result.opted_out is False
    assert [suggestion.member_id for suggestion in result.suggestions] == [
        two_shared_tags_member_id,
        one_shared_tag_member_id,
    ]
    assert result.suggestions[0].shared_tags == ["AI", "Python"]
    assert result.suggestions[0].score == 2
    assert active_member_id not in [
        suggestion.member_id for suggestion in result.suggestions
    ]


def test_opted_out_members_receive_no_suggestions(mock_get_session):
    """Opted-out members receive no suggestions."""
    active_member_id = create_member(
        mock_get_session,
        email="a",
        tags=["cybernetics"],
        matching_opt_out=True,
    )
    create_member(mock_get_session, email="b", tags=["cybernetics"])

    result = MemberMatchingModule().get_suggestions(active_member_id)

    assert result.opted_out is True
    assert result.suggestions == []


def test_opted_out_candidates_are_not_suggested(mock_get_session):
    """Opted-out members are not suggested."""
    active_member_id = create_member(mock_get_session, email="a", tags=["cybernetics"])
    opted_out_member_id = create_member(
        mock_get_session,
        email="b",
        tags=["cybernetics"],
        matching_opt_out=True,
    )

    result = MemberMatchingModule().get_suggestions(active_member_id)

    assert opted_out_member_id not in [
        suggestion.member_id for suggestion in result.suggestions
    ]


def test_dismissal_hides_suggestion_until_cooldown_expires(
    mock_get_session,
    monkeypatch,
):
    """Dismissed suggestions are hidden until cooldown expires."""
    active_member_id = create_member(mock_get_session, email="a", tags=["cybernetics"])
    suggested_member_id = create_member(
        mock_get_session, email="b", tags=["cybernetics"]
    )

    now = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
    # Replace _now() with the test time
    monkeypatch.setattr(
        MemberMatchingModule,
        "_now",
        staticmethod(lambda: now),
    )

    with mock_get_session() as session:
        session.add(
            model.Module(
                module_name=MemberMatchingModule.MODULE_NAME,
                config={
                    "dismissal_days": 1,
                    "maximum_suggestions": 20,
                },
            )
        )
        session.commit()

    module = MemberMatchingModule()

    # Active member dismisses the suggestion
    module.dismiss_suggestion(active_member_id, suggested_member_id)

    # No suggestions should be returned
    assert module.get_suggestions(active_member_id).suggestions == []

    # Set the time to the next day + 1 sec
    monkeypatch.setattr(
        MemberMatchingModule,
        "_now",
        staticmethod(lambda: now + timedelta(days=1, seconds=1)),
    )

    result = module.get_suggestions(active_member_id)

    assert [suggestion.member_id for suggestion in result.suggestions] == [
        suggested_member_id,
    ]


def test_empty_tags_return_no_suggestions(mock_get_session):
    """A member needs profile tags before the system can suggest matches."""
    active_member_id = create_member(mock_get_session, email="a", tags=[])
    create_member(mock_get_session, email="b", tags=["cybernetics"])

    result = MemberMatchingModule().get_suggestions(active_member_id)

    assert result.opted_out is False
    assert result.suggestions == []


def test_dismissing_unknown_member_returns_not_found(mock_get_session):
    """Dismissal rejects a member that does not exist."""
    active_member_id = create_member(mock_get_session, email="a", tags=["cybernetics"])

    # Dismissing an unknown member should raise a 404
    with pytest.raises(HTTPException) as error:
        MemberMatchingModule().dismiss_suggestion(
            active_member_id,
            suggested_member_id=9999,
        )

    assert error.value.status_code == 404


def test_member_matching_routes(
    test_server: TestClient,
    mock_get_session,
    authenticate_member,
):
    """Routes use authenticated identity."""
    active_member_id = create_member(mock_get_session, email="a", tags=["cybernetics"])
    suggested_member_id = create_member(
        mock_get_session, email="b", tags=["cybernetics"]
    )

    authenticate_member(active_member_id)

    suggestions_response = test_server.get("/member-matching")
    assert suggestions_response.status_code == 200
    assert suggestions_response.json()["suggestions"][0]["member_id"] == (
        suggested_member_id
    )

    dismiss_response = test_server.post(
        "/member-matching/dismiss",
        json={"suggested_member_id": suggested_member_id},
    )
    assert dismiss_response.status_code == 200

    opt_out_response = test_server.post("/member-matching/opt-out")
    assert opt_out_response.status_code == 200
    assert opt_out_response.json() == {"matching_opt_out": True}

    opt_in_response = test_server.post("/member-matching/opt-in")
    assert opt_in_response.status_code == 200
    assert opt_in_response.json() == {"matching_opt_out": False}
