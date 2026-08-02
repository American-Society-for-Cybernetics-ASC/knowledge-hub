from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("postgresql+psycopg2://postgres:password@localhost:5432/database")

def get_session() -> Session:
    return Session(engine)