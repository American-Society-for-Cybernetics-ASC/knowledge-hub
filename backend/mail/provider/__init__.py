from abc import abstractmethod

from utils import BaseModel
from mail.model import Email


class MailProviderInterface(BaseModel):
    @abstractmethod
    def send_mail(self, mail: Email): ...
