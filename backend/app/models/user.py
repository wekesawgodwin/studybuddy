# backend/app/models/user.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class User(Base):
    """
    Stores identity and authentication metadata.

    We do NOT store a password. Authentication is entirely OTP-based.
    auth_provider identifies how the user authenticates ("email_otp").
    auth_subject_id is the unique identifier from the provider — for
    email OTP this is simply the user's email address.
    """
    __tablename__ = "users"

    # Primary key — UUID is preferred over integer for security
    # (sequential IDs allow enumeration attacks)
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    # The authentication method used — always "email_otp" in this system
    auth_provider = Column(String(50), nullable=False, default="email_otp")

    # The unique identifier from the provider.
    # For email OTP this is the email address itself.
    # unique=True enforces one account per email.
    auth_subject_id = Column(String(255), unique=True, nullable=False)

    # The user's email address — stored separately from auth_subject_id
    # so the schema supports future providers (e.g. Google SSO) where
    # auth_subject_id would be a Google user ID, not an email.
    email = Column(String(255), unique=True, nullable=False)

    # Soft delete / account suspension flag.
    # Set to False to disable a user without deleting their data.
    is_active = Column(Boolean, default=True, nullable=False)

    # Audit timestamps
    created_at = Column(DateTime, default=datetime.timezone.utc, nullable=False)
    updated_at = Column(DateTime, default=datetime.timezone.utc, onupdate=datetime.timezone.utc)