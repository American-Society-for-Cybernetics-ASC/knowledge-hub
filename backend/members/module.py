from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from membership.model import MemberStatus
import database
from database import model as database_model
from members.model import Affiliation, MemberProfile, MemberSearchResult, ProfileContent, ProfileUpdate


class MemberNotFoundError(LookupError):
    """Raised when a requested member is not found."""


class MembersModule:
    """Business logic for member profile retrieval and updates."""

    @staticmethod
    def _serialize_profile(
        member: database_model.Member,
        profile: database_model.Profile,
    ) -> MemberProfile:
        """
        Helper method to serialize the profile into the API model.

        1. Get the content from the profile.
        2. Get the tags from the profile.
        3. Return the serialized profile.
        """
        content = ProfileContent.model_validate(profile.content or {})
        tags = ProfileUpdate.model_validate({"tags": profile.tags or []}).tags or []

        return MemberProfile(
            member_id=member.auth_user_id,
            status=MemberStatus.calc_expiry(member.membership_expires),
            content=content,
            tags=tags,
        )

    @staticmethod
    def _get_affiliations(content: ProfileContent) -> list[Affiliation]:
        """Collect affiliation metadata"""
        affiliations: list[Affiliation] = []

        for metadata in content.metadata.values():
            if metadata.type == "affiliation":
                affiliations.append(metadata.value)
            elif metadata.type == "affiliations":
                affiliations.extend(metadata.value)

        return affiliations

    @staticmethod
    def _matches_query(value: str | None, query: str) -> bool:
        """Return whether a text values contains the query."""
        return value is not None and query in value.casefold()

    def search_members(self, query: str) -> list[MemberSearchResult]:
        """Search current member profiles by display name, tag or affiliation."""
        normalized_query = query.strip().casefold()

        if not normalized_query:
            return []

        with database.get_session() as session:
            current_members = session.scalars(
                select(database_model.Member)
                .join(database_model.Profile)
                .where(
                    database_model.Member.membership_expires 
                    > datetime.now(timezone.utc)
                )
            ).all()

            results: list[tuple[int, MemberSearchResult]] = []

            for member in current_members:
                profile = member.profile

                if profile is None:
                    continue
                
                member_profile = self._serialize_profile(member, profile)
                display_name = member_profile.content.identity.display_name
                affiliations = self._get_affiliations(member_profile.content)

                name_matches = self._matches_query(
                    display_name, 
                    normalized_query,
                )
                tag_matches = any(
                    self._matches_query(tag, normalized_query) 
                    for tag in member_profile.tags
                )
                affiliation_matches = any(
                    self._matches_query(
                        affiliation.organisation,
                        normalized_query,
                    )
                    or self._matches_query(
                        affiliation.role,
                        normalized_query,
                    )
                    for affiliation in affiliations
                )
                
                if not (name_matches or tag_matches or affiliation_matches):
                    continue
                
                # Prefer name matches, remaining results sort by name and member ID.
                result_priority = 0 if name_matches else 1

                results.append(
                    (
                        result_priority,
                        MemberSearchResult(
                            member_id=member.auth_user_id,
                            display_name=display_name,
                            status=member_profile.status,
                            tags=member_profile.tags,
                            affiliations=affiliations,
                        ),
                    )
                )

        results.sort(
            key=lambda item: (
                item[0],
                (item[1].display_name or "").casefold(),
                item[1].member_id,
            )
        )

        return [result for _, result in results]

    @staticmethod
    def _get_or_create_profile(
        session: Any,
        member: database_model.Member,
    ) -> database_model.Profile:
        """
        Helper method to get or create the profile for a member.

        1. If the member has a profile, return it.
        2. If the member does not have a profile, create a new one.
        3. Return the profile.
        """
        if member.profile is not None:
            return member.profile

        profile = database_model.Profile(
            member_id=member.auth_user_id,
            content=ProfileContent().model_dump(mode="json"),
            tags=[],
        )
        session.add(profile)
        session.flush()
        return profile

    def get_profile(self, member_id: int) -> MemberProfile:
        """
        Method to get member profile.

        1. Get the member from the database.
        2. If the member is not found, raise a MemberNotFoundError.
        3. Get or create the profile for the member.
        4. Return the serialized profile.
        """
        with database.get_session() as session:
            member = session.get(database_model.Member, member_id)

            if member is None:
                raise MemberNotFoundError(member_id)

            profile = self._get_or_create_profile(session, member)
            session.commit()

            return self._serialize_profile(member, profile)

    def update_profile(
        self,
        member_id: int,
        update: ProfileUpdate,
    ) -> MemberProfile:
        """
        Method to update member profile.

        1. Get the member from the database.
        2. If the member is not found, raise a MemberNotFoundError.
        3. Get or create the profile for the member.
        4. Update the profile with the new content.
        5. Return the serialized profile.
        """
        with database.get_session() as session:
            member = session.get(database_model.Member, member_id)

            if member is None:
                raise MemberNotFoundError(member_id)

            profile = self._get_or_create_profile(session, member)
            current_content = ProfileContent.model_validate(profile.content or {})
            content_data = current_content.model_dump(mode="json")
            update_data = update.model_dump(exclude_unset=True, mode="json")

            if "identity" in update_data:
                identity_update = update_data.pop("identity") or {}
                identity_data = dict(content_data["identity"])
                identity_data.update(identity_update)
                content_data["identity"] = identity_data

            if "metadata" in update_data:
                metadata_update = update_data.pop("metadata") or {}
                metadata_data = dict(content_data["metadata"])
                metadata_data.update(metadata_update)
                content_data["metadata"] = metadata_data

            if "tags" in update_data:
                profile.tags = update_data.pop("tags") or []

            # This is to ensure that the collection fields are always a list.
            collection_fields = {
                "research_interests",
                "expertise",
            }
            for field in collection_fields:
                if field in update_data and update_data[field] is None:
                    update_data[field] = []

            # Update the profile content with the new data.
            content_data.update(update_data)
            profile.content = ProfileContent.model_validate(content_data).model_dump(
                mode="json"
            )

            session.commit()
            session.refresh(profile)

            return self._serialize_profile(member, profile)