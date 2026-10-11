from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from settings import SETTINGS

if not SETTINGS.testing:
    engine = create_engine(
        SETTINGS.database_url, connect_args={"options": "-c timezone=utc"}
    )


def get_session() -> Session:
    if SETTINGS.testing:
        raise AssertionError("get_session should always be mocked in tests")

    return Session(engine)


@contextmanager
def with_transaction() -> Generator[Session]:
    session = get_session()
    with session.begin():
        yield session
