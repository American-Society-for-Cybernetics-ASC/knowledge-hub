from utils import BaseModel


class EmailTemplateData(BaseModel):
    name: str
    subject: str
    body: str
    variables: list[str]


class EmailTemplateUpdate(BaseModel):
    subject: str | None = None
    body: str | None = None