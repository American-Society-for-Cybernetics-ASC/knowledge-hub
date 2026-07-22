from pydantic import BaseModel, Field


class SynthesisInput(BaseModel):
    """Structured input prepared by backend modules before calling Claude."""

    activity_data: str = Field(min_length=1)


class SynthesisOutput(BaseModel):
    """Text returned by Claude after a content synthesis request."""

    text: str
