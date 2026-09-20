from typing import Optional
from utils import BaseModel


class MailingList(BaseModel):
    mailing_list_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    email: Optional[str] = None


class MailingListMember(BaseModel):
    """represents any email address on a mailing list including non-members emails"""

    mailing_list_id: int
    email: str
    member_id: Optional[int] = None
