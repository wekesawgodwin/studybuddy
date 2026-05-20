
"""This file sets up the SQLAlchemy engine and provides the `get_db` dependency
that every route handler will use to access the database."""
# backend/app/db/session.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Import all models here so SQLAlchemy can resolve every relationship
# before any mapper is used. Without this, models that reference each
# other via relationship() fail with "failed to locate a name" errors
# when the mapper initialises — especially in standalone scripts like
# create_superuser.py that do not go through FastAPI's startup sequence.
#
# The noqa comments suppress "imported but unused" linter warnings —
# these imports are intentional side effects, not direct usage.
from app.models.user import User               # noqa: F401, E402
from app.models.otp import OTPCode             # noqa: F401, E402
from app.models.role import AdminPermission    # noqa: F401, E402
from app.models.course import (                # noqa: F401, E402
    Course, Module, SubModule, Topic
)