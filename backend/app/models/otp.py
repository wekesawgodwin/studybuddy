# backend/app/models/otp.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class OTPCode(Base):
    """
    Stores one-time password codes used for passwordless login.

    Security design:
    - We NEVER store the raw OTP. We store a bcrypt hash of it.
      This means even if the database is compromised, the OTPs are useless.
    - Each OTP has a 10-minute expiry. After that it cannot be used.
    - Each OTP can only be used once. The `is_used` flag prevents replay attacks.
    - We allow only one active OTP per email at a time. When a new OTP is
      requested we invalidate all previous ones for that email.
    """
    __tablename__ = "otp_codes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    # The email this OTP was sent to
    email = Column(String(255), nullable=False, index=True)

    # The bcrypt hash of the 6-digit OTP code.
    # We index nothing here — bcrypt hashes are not comparable without
    # the verify function, so indexing would provide no benefit.
    otp_hash = Column(String(255), nullable=False)

    # When this OTP expires. Set to utcnow + 10 minutes at creation time.
    expires_at = Column(DateTime, nullable=False)

    # Once the user successfully verifies this OTP we set is_used = True.
    # This prevents the same OTP from being submitted a second time
    # (replay attack prevention).
    is_used = Column(Boolean, default=False, nullable=False)

    # Audit timestamp
    created_at = Column(DateTime, default=datetime.timezone.utc, nullable=False)