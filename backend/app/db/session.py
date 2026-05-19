
"""This file sets up the SQLAlchemy engine and provides the `get_db` dependency
that every route handler will use to access the database."""
# backend/app/db/session.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

# Load .env file for local development.
# On Railway, environment variables are injected directly — load_dotenv
# simply does nothing when the variables are already set, so it is safe
# to call in all environments.
load_dotenv()

# Read the database URL from the environment.
# Locally this comes from your .env file.
# On Railway this is auto-injected by the Postgres service reference.
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Create the SQLAlchemy engine.
# pool_pre_ping=True means SQLAlchemy will test the connection before using
# it, which prevents errors after the database restarts or idles out.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal is the class we use to create database sessions.
# autocommit=False means we control when transactions are committed.
# autoflush=False means SQLAlchemy won't flush pending changes automatically.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base is the parent class all SQLAlchemy models inherit from.
class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI dependency that yields a database session.

    Usage in any route:
        def my_route(db: Session = Depends(get_db)):
            ...

    The `finally` block guarantees the session is always closed,
    even if an exception is raised inside the route handler.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()