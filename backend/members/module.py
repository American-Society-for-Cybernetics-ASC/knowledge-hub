from typing import Any

import database
from database import model as database_model
from members.model import MemberProfile, ProfileContent, ProfileSettings, ProfileUpdate

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
            member_id=member.member_id,
            status=member.status,
            content=content,
            tags=tags,
        )

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
            member_id=member.member_id,
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

            # Update the profile content with the new data.
            content_data.update(update_data)
            profile.content = ProfileContent.model_validate(content_data).model_dump(
                mode = "json"
            )   

            session.commit()
            session.refresh(profile)

            return self._serialize_profile(member, profile)