from typing import Callable

import pytest
from sqlalchemy.orm import Session

from database import model
from members.model import ProfileUpdate
from members.module import MemberNotFoundError, MembersModule


def create_member(get_session: Callable[[], Session]) -> int:
    """Create a basic member and return its database ID."""

    with get_session() as session:
        member = model.Member(status="active")
        session.add(member)
        session.commit()
        session.refresh(member)

        return member.auth_user_id


def test_get_profile_creates_empty_profile(mock_get_session):
    """Getting a profile creates one when the member has no profile yet."""

    member_id = create_member(mock_get_session)

    profile = MembersModule().get_profile(member_id)

    assert profile.member_id == member_id
    assert profile.status == "active"
    assert profile.content.personal_statement is None
    assert profile.content.research_interests == []
    assert profile.content.expertise == []
    assert profile.tags == []

    # Confirm that new profile was saved to the db
    with mock_get_session() as session:
        stored_profile = session.get(model.Profile, member_id)
        assert stored_profile is not None


def test_update_profile(mock_get_session):
    """A member can update their profile content and matching tags."""

    member_id = create_member(mock_get_session)

    update = ProfileUpdate(
        identity={
            "display_name": "Son",
            "location": "Perth",
        },
        personal_statement="Interested in cybernetics.",
        research_interests=["Cybernetics"],
        expertise=["Python", "SQL"],
        tags=["cybernetics", "PYTHON", " sql "],
    )

    profile = MembersModule().update_profile(member_id, update)

    assert profile.content.identity.display_name == "Son"
    assert profile.content.identity.location == "Perth"
    assert profile.content.personal_statement == "Interested in cybernetics."
    assert profile.content.research_interests == ["Cybernetics"]
    assert profile.content.expertise == ["Python", "SQL"]

    # Trim, convert to lowercase, remove duplicates
    assert profile.tags == ["cybernetics", "python", "sql"]


def test_update_preserves_existing_fields(mock_get_session):
    """Updating one field does not affect other fields."""

    member_id = create_member(mock_get_session)
    members = MembersModule()

    members.update_profile(
        member_id,
        ProfileUpdate(
            identity={
                "display_name": "Son",
                "location": "Perth",
            },
            expertise=["Python"],
        ),
    )

    updated_profile = members.update_profile(
        member_id,
        ProfileUpdate(
            personal_statement="Updated statement.",
        ),
    )

    assert updated_profile.content.identity.display_name == "Son"
    assert updated_profile.content.identity.location == "Perth"
    assert updated_profile.content.expertise == ["Python"]
    assert updated_profile.content.personal_statement == "Updated statement."


def test_profile_update_persistent(mock_get_session):
    """Profile updates remain available in later sessions."""

    member_id = create_member(mock_get_session)
    members = MembersModule()

    members.update_profile(
        member_id,
        ProfileUpdate(
            personal_statement="Saved statement.",
            tags=["cybernetics"],
        ),
    )

    profile = members.get_profile(member_id)

    assert profile.content.personal_statement == "Saved statement."
    assert profile.tags == ["cybernetics"]


def test_missing_member_raises_error():
    """Getting a profile for a missing member raises an error."""

    with pytest.raises(MemberNotFoundError):
        MembersModule().get_profile(999)


# Wrap affiliations in metadata
def test_invalid_affiliation_years():
    """Affiliation cannot finish before it starts."""
    with pytest.raises(ValueError):
        ProfileUpdate(
            metadata={
                "current_affiliation": {
                    "type": "affiliation",
                    "value": {
                        "organisation": "Example University",
                        "start_year": 2025,
                        "end_year": 2020,
                    },
                }
            }
        )
