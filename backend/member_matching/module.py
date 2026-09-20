from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy import select

import database
from database import model

from .config import MemberMatchingConfig
from .schema import (
    DismissMatchResult,
    MemberMatchingSuggestion,
    MemberMatchSuggestionsResult,
    MatchingPreferenceResult,
)


class MemberMatchingModule:
    """
    Suggestions are calculated from overlapping profile tags when requested.

    DB only stores dismissals, not every generated match.
    """

    MODULE_NAME = "member_matching"

    @staticmethod
    def _now() -> datetime:
        """Return UTC time; kept separate for testing."""
        return datetime.now(timezone.utc)

    @staticmethod
    def _normalize_tags(tags: object) -> dict[str, str]:
        """Convert raw JSON profile tags into unique values."""

        if not isinstance(tags, list):
            return {}

        normalized: dict[str, str] = {}

        for tag in tags:
            if not isinstance(tag, str):
                continue

            cleaned_tag = " ".join(tag.split())
            comparison_key = cleaned_tag.casefold()

            if cleaned_tag and comparison_key not in normalized:
                normalized[comparison_key] = cleaned_tag

        return normalized

    def get_config(self) -> MemberMatchingConfig:
        """Load matching config, creating MVP defaults when absent."""
        with database.get_session() as session:
            config_record = session.scalar(
                select(model.Module).where(model.Module.module_name == self.MODULE_NAME)
            )

            if config_record is None:
                config = MemberMatchingConfig()
                config_record = model.Module(
                    module_name=self.MODULE_NAME,
                    config=config.model_dump(mode="json"),
                )
                session.add(config_record)
                session.commit()

            return MemberMatchingConfig.model_validate(config_record.config)

    @staticmethod
    def _display_name(profile: model.Profile) -> str | None:
        """Return the public display name, without exposing full profile content."""
        if not isinstance(profile.content, dict):
            return None

        identity = profile.content.get("identity")
        if not isinstance(identity, dict):
            return None

        display_name = identity.get("display_name")
        return display_name if isinstance(display_name, str) else None

    @staticmethod
    def _is_still_dismissed(
        dismissed_at: datetime,
        cooldown_cutoff: datetime,
    ) -> bool:
        """Check if a dismissed suggestion is still in the cooldown period."""
        if dismissed_at.tzinfo is None:
            dismissed_at = dismissed_at.replace(tzinfo=timezone.utc)

        # Return either as naive or UTC aware
        return dismissed_at >= cooldown_cutoff

    def get_suggestions(
        self,
        member_id: int,
    ) -> MemberMatchSuggestionsResult:
        """Return suggestions ranked by no. of shared tags."""
        config = self.get_config()

        with database.get_session() as session:
            active_member = session.get(model.Member, member_id)

            # If member does not exist
            if active_member is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Member not found",
                )

            # If member does not have a profile
            active_profile = active_member.profile
            if active_profile is None:
                return MemberMatchSuggestionsResult(
                    opted_out=False,
                    suggestions=[],
                )

            # If member has disabled matching
            if active_profile.matching_opt_out:
                return MemberMatchSuggestionsResult(
                    opted_out=True,
                    suggestions=[],
                )

            # Get their tags and normalize
            active_tags = self._normalize_tags(active_profile.tags)
            if not active_tags:
                return MemberMatchSuggestionsResult(
                    opted_out=False,
                    suggestions=[],
                )

            # Calc the dismissal cooldown
            cooldown_cutoff = self._now() - timedelta(days=config.dismissal_days)

            # Get all dismissals for the member
            dismissals = session.scalars(
                select(model.MemberMatching).where(
                    model.MemberMatching.active_member_id == member_id
                )
            ).all()

            # Create a set of dismissed member IDs
            suppressed_member_ids = {
                dismissal.suggested_member_id
                for dismissal in dismissals
                if self._is_still_dismissed(
                    dismissal.dismissed_at,
                    cooldown_cutoff,
                )
            }

            # Get all eligible candidates
            candidates = session.scalars(
                select(model.Member)
                .join(model.Profile)
                .where(
                    model.Member.user_id != member_id,
                    model.Profile.matching_opt_out.is_(False),
                    model.Member.due_date > datetime.now(timezone.utc),
                )
            ).all()

            # Create a list of suggestions
            suggestions: list[MemberMatchingSuggestion] = []
            processed_member_ids: set[int] = set()

            for candidate in candidates:
                # Prevent duplicate candidates
                if candidate.user_id in processed_member_ids:
                    continue
                processed_member_ids.add(candidate.user_id)

                # Prevent dismissed candidates
                if candidate.user_id in suppressed_member_ids:
                    continue

                if candidate.profile is None:
                    continue

                # Normalize candidate tags
                candidate_tags = self._normalize_tags(candidate.profile.tags)
                # Get shared tags
                shared_tag_keys = active_tags.keys() & candidate_tags.keys()

                # Skip if they don't share tags
                if not shared_tag_keys:
                    continue

                # Clean the shared tags
                shared_tags = sorted(
                    (active_tags[tag_key] for tag_key in shared_tag_keys),
                    key=str.casefold,
                )

                # Create the suggestion
                suggestions.append(
                    MemberMatchingSuggestion(
                        member_id=candidate.user_id,
                        display_name=self._display_name(candidate.profile),
                        shared_tags=shared_tags,
                        score=len(shared_tags),
                    )
                )

            # Sort descending by score, member ID as tie breaker
            suggestions.sort(
                key=lambda suggestion: (-suggestion.score, suggestion.member_id)
            )

            # Return the suggestions, depends on max config
            return MemberMatchSuggestionsResult(
                opted_out=False, suggestions=suggestions[: config.maximum_suggestions]
            )

    def set_opt_out(
        self,
        member_id: int,
        matching_opt_out: bool,
    ) -> MatchingPreferenceResult:
        """Enable or disable matching for a member."""
        with database.get_session() as session:
            member = session.get(model.Member, member_id)

            if member is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Member not found",
                )

            if member.profile is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member profile not found",
                )

            member.profile.matching_opt_out = matching_opt_out
            session.commit()

            return MatchingPreferenceResult(
                matching_opt_out=matching_opt_out,
            )

    def dismiss_suggestion(
        self,
        member_id: int,
        suggested_member_id: int,
    ) -> DismissMatchResult:
        """Hide a suggestion for configured cooldown period."""
        if member_id == suggested_member_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot dismiss self",
            )

        # Find both members
        with database.get_session() as session:
            active_member = session.get(model.Member, member_id)
            suggested_member = session.get(model.Member, suggested_member_id)

            if active_member is None or suggested_member is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Member not found",
                )

            # Check if dismissal already exists
            dismissal = session.scalar(
                select(model.MemberMatching).where(
                    model.MemberMatching.active_member_id == member_id,
                    model.MemberMatching.suggested_member_id == suggested_member_id,
                )
            )

            # If dismissal does not exist, create it
            if dismissal is None:
                dismissal = model.MemberMatching(
                    active_member_id=member_id,
                    suggested_member_id=suggested_member_id,
                    dismissed_at=self._now(),
                )
                session.add(dismissal)
            else:
                # Repeating dismissal restarts cooldown
                dismissal.dismissed_at = self._now()

            session.commit()

            return DismissMatchResult(
                suggested_member_id=suggested_member_id,
            )
