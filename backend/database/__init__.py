import sqlalchemy
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://username:password@db:5432/database")


def connect() -> sqlalchemy.Connection:
    return engine.connect()
