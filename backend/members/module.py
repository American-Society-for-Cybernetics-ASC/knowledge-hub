from typing import Any

import database
from database import model as database_model
from members.model import MemberProfile, ProfileContent, ProfileSettings, ProfileUpdate

class MemberNotFoundError(LookupError):
    """Raised when a requested member is not found."""

class MembersModule:
    """Business logic for member profile retrieval and updates."""

    # Private helper method to serialize the profile into the API model.
    # 1. Get the content from the profile.
    # 2. Get the tags from the profile.
    # 3. Return the serialized profile.
    @staticmethod
    def _serialize_profile(
        member: database_model.Member,
        profile: database_model.Profile,
    ) -> MemberProfile:
        content = ProfileContent.model_validate(profile.content or {})
        tags = ProfileUpdate.model_validate({"tags": profile.tags or []}).tags or []

        return MemberProfile(
            member_id=member.member_id,
            status=member.status,
            content=content,
            tags=tags,
        )

    # Private helper method to get or create the profile for a member.
    # 1. If the member has a profile, return it.
    # 2. If the member does not have a profile, create a new one.
    # 3. Return the profile.
    @staticmethod
    def _get_or_create_profile(
        session: Any,
        member: database_model.Member,
    ) -> database_model.Profile:
        if member.profile is not None:
            return member.profile

        profile = database_model.Profile(
            member_id=member.member_id,
            content=ProfileContent().model_dump(mode="json"),
            tags=[],
        )
        session.add(profile)
        session.flush()
        return profile

    # Public method to get member profile.
    def get_profile(self, member_id: int) -> MemberProfile:
        with database.get_session() as session:
            member = session.get(database_model.Member, member_id)

            if member is None:
                raise MemberNotFoundError(member_id)

            profile = self._get_or_create_profile(session, member)
            session.commit()

            return self._serialize_profile(member, profile)

    # Public method to update member profile.
    def update_profile(
        self,
        member_id: int,
        update: ProfileUpdate,
    ) -> MemberProfile:
        with database.get_session() as session:
            member = session.get(database_model.Member, member_id)

            if member is None:
                raise MemberNotFoundError(member_id)

            profile = self._get_or_create_profile(session, member)
            current_content = ProfileContent.model_validate(profile.content or {})
            content_data = current_content.model_dump(mode="json")
            update_data = update.model_dump(exclude_unset=True, mode = "json")

            if "identity" in update_data:
                identity_update = update_data.pop("identity") or {}
                identity_data = dict(content_data["identity"])
                identity_data.update(identity_update)
                content_data["identity"] = identity_data

            if "settings" in update_data:
                settings_update = update_data.pop("settings") or {}
                settings_data = dict(content_data["settings"])
                settings_data.update(settings_update)
                content_data["settings"] = settings_data

            if "tags" in update_data:
                profile.tags = update_data.pop("tags") or []    

            # This is to ensure that the collection fields are always a list.
            collection_fields = {
                "research_interests",
                "expertise",
                "affiliations",
                "publications",
            }

            for field in collection_fields:
                if field in update_data and update_data[field] is None:
                    update_data[field] = []

            content_data.update(update_data)
            profile.content = ProfileContent.model_validate(content_data).model_dump(
                mode = "json"
            )

            session.commit()
            session.refresh(profile)

            return self._serialize_profile(member, profile)