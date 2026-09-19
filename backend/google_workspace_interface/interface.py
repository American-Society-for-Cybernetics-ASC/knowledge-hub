from abc import abstractmethod
from utils import BaseModel
from mailing_list.model import MailingList

class MailingListInterface(BaseModel):
    """
    Abstract interface for mailing list providers.
    Implemented by GoogleWorkspaceService
    Allows the mailing list provider to be swapped out independently of the rest of the platform
    """
    @abstractmethod
    def get(self) -> list[MailingList]:
        """returns all Google Workspace mailing lists"""
        ...

    @abstractmethod
    def add_user(self, user: str, mailing_list: MailingList) -> None:
        """
        Adds a user to a mailing list.
        """
        ...

    @abstractmethod
    def remove_user(self, user: str, mailing_list: MailingList) -> None:
        """Remove a user from a mailing list
        """
        ...

