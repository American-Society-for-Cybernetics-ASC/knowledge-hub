from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from settings import SETTINGS

engine = create_engine("postgresql+psycopg2://username:password@db:5432/database")


def get_session() -> Session:
    if SETTINGS.testing:
        raise AssertionError("get_session should always be mocked in tests")
    return Session(engine)
