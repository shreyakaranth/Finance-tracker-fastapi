"""
Sets up the SQLite database connection and gives us a way to
open/close a DB session for each request.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./finance.db"

# check_same_thread=False is needed only for SQLite + FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency: opens a DB session for one request,
    always closes it afterward (even if an error happens).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
