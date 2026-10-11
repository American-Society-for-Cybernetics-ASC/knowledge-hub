from uuid import UUID
import uuid

from mail.model import Email


class MockMailManager:
    ids: list[UUID] = []
    _fails = 0
    _sent_mail: list[Email] = []

    def send_mail(self, mail: Email):
        if self._fails > 0:
            self._fails -= 1
            raise Exception(f"test-induced error: {self._fails} errors remain")
        self._sent_mail.append(mail)

    def register_mock(self, id: uuid.UUID):
        self.ids.append(id)

    def fail_next_n_mail(self, n: int):
        self._fails += n

    def sent_mail(self) -> list[Email]:
        return self._sent_mail
