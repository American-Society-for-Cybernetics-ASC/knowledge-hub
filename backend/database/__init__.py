from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from settings import SETTINGS


class LocalDatabaseInterface:
    def __init__(self):
        self.engine = None

    def connect(self):
        self.engine = create_engine(
            "postgresql+psycopg2://username:password@db:5432/database",
            connect_args={"options": "-c timezone=utc"},
        )
        return self.engine


class SupabaseDatabaseInterface:
    def __init__(self):
        self.engine = None

    def connect(self):
        self.engine = create_engine(
            SETTINGS.supabase_database_url, connect_args={"options": "-c timezone=utc"}
        )
        return self.engine


def get_session() -> Session:
    if SETTINGS.testing:
        raise AssertionError("get_session should always be mocked in tests")

    if SETTINGS.local_deployment:
        engine = LocalDatabaseInterface().connect()
    else:
        engine = SupabaseDatabaseInterface().connect()

    return Session(engine)
