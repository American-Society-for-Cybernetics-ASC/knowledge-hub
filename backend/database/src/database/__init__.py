from sqlalchemy import create_engine
import sqlalchemy

engine = create_engine("postgresql+psycopg2://username:password@db:5432/database")


def connect() -> sqlalchemy.Connection:
    return engine.connect()
