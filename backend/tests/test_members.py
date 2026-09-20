import datetime
from typing import Callable

import pytest
from sqlalchemy.orm import Session

from membership.model import MemberStatus
from database import model
from members.model import ProfileUpdate
from members.module import MemberNotFoundError, MembersModule
from fastapi.testclient import TestClient
from main import app
from members.routes import get_current_member_id


def create_member(
    get_session: Callable[[], Session],
    email: str = "example@example.com",
) -> int:
    """Create a basic member and return its database ID."""

    with get_session() as session:
        auth_user = model.AuthUser(email=email)
        session.add(auth_user)
        session.commit()
        session.refresh(auth_user)

        member = model.Member(
            auth_user=auth_user,
            due_date=datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=100),
            cancelled=False,
        )
        session.add(member)
        session.commit()
        session.refresh(member)

        return member.auth_user_id


def test_get_profile_creates_empty_profile(mock_get_session):
    """Getting a profile creates one when the member has no profile yet."""

    member_id = create_member(mock_get_session)

    profile = MembersModule().get_profile(member_id)

    assert profile.member_id == member_id
    assert profile.status == MemberStatus.CURRENT
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


@pytest.fixture
def authenticate_member():
    """Override member authentication for testing."""

    def authenticate(member_id: int) -> None:
        app.dependency_overrides[get_current_member_id] = lambda: member_id

    yield authenticate

    app.dependency_overrides.pop(get_current_member_id, None)


def test_get_member_profile_by_id(mock_get_session, authenticate_member):
    """An authenticated member can view another member's profile."""
    requesting_member_id = create_member(mock_get_session, "requesting@example.com")
    target_member_id = create_member(mock_get_session, "target@example.com")

    MembersModule().update_profile(
        target_member_id,
        ProfileUpdate(
            identity={"display_name": "Sonion Ring"},
            personal_statement="Interested in cybernetics.",
            tags=["cybernetics"],
        ),
    )

    authenticate_member(requesting_member_id)
    response = TestClient(app).get(f"/members/{target_member_id}")

    assert response.status_code == 200
    assert response.json()["member_id"] == target_member_id
    assert response.json()["content"]["identity"]["display_name"] == "Sonion Ring"
    assert response.json()["tags"] == ["cybernetics"]


def test_get_member_profile_returns_expired_status(
    mock_get_session,
    authenticate_member,
):
    """A profile's status is calculated from membership expiration."""
    requesting_member_id = create_member(mock_get_session, "requesting@example.com")
    expired_member_id = create_member(mock_get_session, "expired@example.com")

    with mock_get_session() as session:
        expired_member = session.get(model.Member, expired_member_id)
        expired_member.due_date = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(days=1)
        session.commit()

    authenticate_member(requesting_member_id)
    response = TestClient(app).get(f"/members/{expired_member_id}")

    assert response.status_code == 200
    assert response.json()["status"] == MemberStatus.EXPIRED


def test_get_member_profile_returns_metadata(
    mock_get_session,
    authenticate_member,
):
    """Profile metadata is returned."""
    requesting_member_id = create_member(mock_get_session, "requesting@example.com")
    target_member_id = create_member(mock_get_session, "target@example.com")
    MembersModule().update_profile(
        target_member_id,
        ProfileUpdate(
            metadata={
                "affiliations": {
                    "type": "affiliations",
                    "value": [
                        {
                            "organisation": "Example University",
                            "role": "Researcher",
                            "start_year": 2024,
                        }
                    ],
                },
                "publications": {
                    "type": "publications",
                    "value": [
                        {
                            "title": "Cybernetics Today",
                            "year": 2025,
                            "doi": "10.1234/example",
                        }
                    ],
                },
            }
        ),
    )
    authenticate_member(requesting_member_id)
    response = TestClient(app).get(f"/members/{target_member_id}")
    assert response.status_code == 200
    metadata = response.json()["content"]["metadata"]
    assert metadata["affiliations"]["value"][0]["organisation"] == "Example University"
    assert metadata["publications"]["value"][0]["title"] == "Cybernetics Today"


def test_get_missing_member_profile_returns_404(
    mock_get_session,
    authenticate_member,
):
    """Requesting an unknown profile returns a clear not-found response."""
    requesting_member_id = create_member(mock_get_session)
    authenticate_member(requesting_member_id)
    response = TestClient(app).get("/members/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"


@pytest.mark.logged_out
def test_get_member_profile_requires_authentication(mock_get_session):
    """Unauthenticated requests cannot view member profiles."""
    member_id = create_member(mock_get_session)
    response = TestClient(app).get(f"/members/{member_id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_search_members_matches_name_tag_and_affiliation(
    mock_get_session,
    authenticate_member,
):
    """Search matches name, tag, affiliation organisation and role."""
    requesting_member_id = create_member(mock_get_session, "requesting@example.com")
    name_member_id = create_member(mock_get_session, "name@example.com")
    tag_member_id = create_member(mock_get_session, "tag@example.com")
    affiliation_member_id = create_member(
        mock_get_session,
        "affiliation@example.com",
    )

    members = MembersModule()
    members.update_profile(
        name_member_id,
        ProfileUpdate(identity={"display_name": "Sonion Ring"}),
    )
    members.update_profile(
        tag_member_id,
        ProfileUpdate(
            identity={"display_name": "Tag Member"},
            tags=["cybernetics"],
        ),
    )
    members.update_profile(
        affiliation_member_id,
        ProfileUpdate(
            identity={"display_name": "Affiliation Member"},
            metadata={
                "affiliations": {
                    "type": "affiliations",
                    "value": [
                        {
                            "organisation": "Curtin University",
                            "role": "Researcher",
                        }
                    ],
                }
            },
        ),
    )

    authenticate_member(requesting_member_id)
    client = TestClient(app)

    name_response = client.get("/members", params={"q": "SONION"})
    assert name_response.status_code == 200
    assert [result["member_id"] for result in name_response.json()] == [name_member_id]

    tag_response = client.get("/members", params={"q": "cyber"})
    assert tag_response.status_code == 200
    assert [result["member_id"] for result in tag_response.json()] == [tag_member_id]

    organisation_response = client.get("/members", params={"q": "curtin"})
    assert organisation_response.status_code == 200
    assert [result["member_id"] for result in organisation_response.json()] == [
        affiliation_member_id
    ]

    role_response = client.get("/members", params={"q": "researcher"})
    assert role_response.status_code == 200
    assert [result["member_id"] for result in role_response.json()] == [
        affiliation_member_id
    ]


def test_search_members_rejects_missing_or_empty_query(
    mock_get_session,
    authenticate_member,
):
    """The endpoint requires a non-empty search query."""
    requesting_member_id = create_member(mock_get_session)
    authenticate_member(requesting_member_id)

    client = TestClient(app)

    missing_query_response = client.get("/members")
    assert missing_query_response.status_code == 422

    empty_query_response = client.get("/members", params={"q": ""})
    assert empty_query_response.status_code == 422


@pytest.mark.logged_out
def test_search_members_requires_authentication():
    """Unauthenticated requests cannot search for members."""
    response = TestClient(app).get("/members", params={"q": "cybernetics"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"
