from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("postgresql+psycopg2://username:password@db:5432/database")


def connect() -> sqlalchemy.Connection:
    return engine.connect()

SessionLocal = sessionmaker = (autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

