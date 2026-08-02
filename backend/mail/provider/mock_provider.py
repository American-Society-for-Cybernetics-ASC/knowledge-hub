from typing import Literal
from pydantic import Field

from . import MailProviderInterface
from mail.model import Email

_fails = 0
_sent_mail: list[Email] = []


class MockMailProvider(MailProviderInterface):
    service_name: Literal["mock"] = Field(default="mock")

    def send_mail(self, mail: Email):
        global _fails
        if _fails > 0:
            _fails -= 1
            raise Exception(f"test-induced error: {_fails} errors remain")
        _sent_mail.append(mail)

    @staticmethod
    def fail_next_n_mail(n: int):
        global _fails
        _fails += n

    @staticmethod
    def sent_mail() -> list[Email]:
        return _sent_mail
