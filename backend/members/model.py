from typing import Annotated, Literal

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


def normalize_string_list(values: list[str]) -> list[str]:
    """Trim values and remove blanks and duplicates."""

    normalized: list[str] = []
    seen: set[str] = set()

    for value in values:
        clean_value = " ".join(value.split())
        key = clean_value.casefold()

        if clean_value and key not in seen:
            seen.add(key)
            normalized.append(clean_value)

    return normalized


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


class MetadataBase(BaseModel):
    """Common config for metadata values."""

    model_config = ConfigDict(extra="forbid")


class StringMetadata(MetadataBase):
    type: Literal["str"]
    value: str = Field(max_length=5000)


class IntegerMetadata(MetadataBase):
    type: Literal["int"]
    value: int


class TagListMetadata(MetadataBase):
    type: Literal["tag_list"]
    value: list[Tag] = Field(default_factory=list, max_length=50)

    @field_validator("value")
    @classmethod
    def normalize_tags(cls, values: list[str]) -> list[str]:
        return [value.lower() for value in normalize_string_list(values)]


class AffiliationMetadata(MetadataBase):
    type: Literal["affiliation"]
    value: Affiliation


class AffiliationsMetadata(MetadataBase):
    type: Literal["affiliations"]
    value: list[Affiliation] = Field(default_factory=list, max_length=20)


class PublicationMetadata(MetadataBase):
    type: Literal["publication"]
    value: ProfilePublication


class PublicationsMetadata(MetadataBase):
    type: Literal["publications"]
    value: list[ProfilePublication] = Field(default_factory=list, max_length=50)


Metadata = Annotated[
    StringMetadata
    | IntegerMetadata
    | TagListMetadata
    | AffiliationMetadata
    | AffiliationsMetadata
    | PublicationMetadata
    | PublicationsMetadata,
    Field(discriminator="type"),
]


class ProfileContent(BaseModel):
    """
    Main profile content.

    Contains no knowledge hub submission or repository links.

    Matching-related fields remain fixed, while optional profile sections
    are stored as typed metadata.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    identity: ProfileIdentity = Field(default_factory=ProfileIdentity)
    personal_statement: str | None = Field(default=None, max_length=5000)

    # Remain fixed for member matching.
    research_interests: list[str] = Field(default_factory=list, max_length=30)
    expertise: list[str] = Field(default_factory=list, max_length=30)

    metadata: dict[str, Metadata] = Field(default_factory=dict)

    # Normalize matching fields.
    @field_validator("research_interests", "expertise")
    @classmethod
    def normalize_matching_fields(cls, values: list[str]) -> list[str]:
        return normalize_string_list(values)


class ProfileUpdate(BaseModel):
    """
    Partial profile update.

    Service layer should merge supplied fields into the existing
    ProfileContent rather than replacing the entire profile.
    """

    model_config = ConfigDict(extra="forbid")

    identity: ProfileIdentity | None = None
    personal_statement: str | None = Field(default=None, max_length=5000)
    research_interests: list[str] | None = Field(default=None, max_length=30)
    expertise: list[str] | None = Field(default=None, max_length=30)
    metadata: dict[str, Metadata] | None = None
    tags: list[Tag] | None = Field(default=None, max_length=50)

    # Normalize matching fields.
    @field_validator("research_interests", "expertise")
    @classmethod
    def normalize_matching_fields(
        cls,
        values: list[str] | None,
    ) -> list[str] | None:
        if values is None:
            return None

        return normalize_string_list(values)

    # Remove duplicate and blank tags.
    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str] | None) -> list[str] | None:
        if tags is None:
            return None

        return [tag.lower() for tag in normalize_string_list(tags)]


class MemberProfile(BaseModel):
    """The API response for a member profile."""

    member_id: int
    status: str
    content: ProfileContent
    tags: list[Tag] = Field(default_factory=list)


class MemberSearchResult(BaseModel):
    """A compact member representation for search results."""

    member_id: int
    display_name: str | None = None
    status: str
    tags: list[Tag] = Field(default_factory=list)
    affiliations: list[Affiliation] = Field(default_factory=list)