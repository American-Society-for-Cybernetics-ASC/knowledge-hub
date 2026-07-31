from typing import Annotated

from pydantic import (
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
    field_validator,
    model_validator,
)

from utils import BaseModel

Tag = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=64),
]

Orcid = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        pattern=r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$",
    ),
]

Doi = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=255,
        pattern=r"^10\.\d{4,9}/\S+$",
    ),
]

class ProfileIdentity(BaseModel):
    """Basic member identity."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    display_name: str | None = Field(default=None, max_length=100)
    pronouns: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=150)
    website: HttpUrl | None = None
    orcid: Orcid | None = None

class Affiliation(BaseModel):
    """An organisation which the member is affiliated with."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    organisation: str = Field(min_length=1, max_length=200)
    role: str | None = Field(default=None, max_length=150)
    start_year: int | None = Field(default=None, ge=1000, le=2100)
    end_year: int | None = Field(default=None, ge=1000, le=2100)

    # Validate the year range.
    @model_validator(mode="after")
    def validate_year_range(self):
        if (
            self.start_year is not None
            and self.end_year is not None
            and self.end_year < self.start_year
        ):
            raise ValueError("end_year must not be earlier than start_year")
        return self


class ProfilePublication(BaseModel):
    """A publication which the member has published."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=500)
    year: int | None = Field(default=None, ge=1000, le=2100)
    doi: Doi | None = None
    url: HttpUrl | None = None

class ProfileSettings(BaseModel):
    """Profile preferences retained for future member-matching work."""

    model_config = ConfigDict(extra="forbid")

    matching_opt_out: bool = False

class ProfileContent(BaseModel):
    """ 
    Main profile content.

    Contains no knowledge hub submission or repository links.      
    """  

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    identity: ProfileIdentity = Field(default_factory=ProfileIdentity)
    personal_statement: str | None = Field(default=None, max_length=5000)
    research_interests: list[str] = Field(default_factory=list, max_length=30)
    expertise: list[str] = Field(default_factory=list, max_length=30)
    affiliations: list[Affiliation] = Field(default_factory=list, max_length=20)
    publications: list[ProfilePublication] = Field(default_factory=list, max_length=50)
    settings: ProfileSettings = Field(default_factory=ProfileSettings)
    
    # Remove duplicate and blank values.
    @field_validator("research_interests", "expertise")
    @classmethod
    def remove_blank_and_duplicate_values(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()

        for value in values:
            clean_value = " ".join(value.split())
            key = clean_value.casefold()

            if not clean_value or key in seen:
                continue

            seen.add(key)
            normalized.append(clean_value)

        return normalized

class ProfileUpdate(BaseModel):
    """
    Partial profile update.

    Serivce layer should merge supplied fields into the existing 
    ProfileContent rather than replacing the entire profile.
    """

    model_config = ConfigDict(extra="forbid")

    identity: ProfileIdentity | None = None
    personal_statement: str | None = Field(default=None, max_length=5000)
    research_interests: list[str] | None = Field(default=None, max_length=30)
    expertise: list[str] | None = Field(default=None, max_length=30)
    affiliations: list[Affiliation] | None = Field(default=None, max_length=20)
    publications: list[ProfilePublication] | None = Field(default=None, max_length=50)
    settings: ProfileSettings | None = None
    tags: list[Tag] | None = Field(default=None, max_length=50)

    # Remove duplicate and blank tags.
    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str] | None) -> list[str] | None:
        if tags is None:
            return None

        normalized: list[str] = []
        seen: set[str] = set()

        for tag in tags:
            clean_tag = " ".join(tag.split()).lower()

            if clean_tag and clean_tag not in seen:
                seen.add(clean_tag)
                normalized.append(clean_tag)

        return normalized

class MemberProfile(BaseModel):
    """The API response for a member profile."""

    model_config = ConfigDict(from_attributes=True)

    member_id: int
    status: str
    content: ProfileContent
    tags: list[Tag] = Field(default_factory=list)
