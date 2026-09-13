from pydantic import BaseModel, Field


class MemberMatchingConfig(BaseModel):
    """Config for member matching"""

    dismissal_days: int = Field(
        default=7,
        ge=0,
        description="No. of days a dismissed suggestion remains hidden.",
    )
    maximum_suggestions: int = Field(
        default=20,
        ge=1,
        description="Maximum number of suggestions to show to a member.",
    )
