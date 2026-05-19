# backend/app/services/auth_service.py
""" The service layer contains all business logic. Route handlers call services;
services call models. This keeps routes thin and logic testable."""
import random
import string
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.otp import OTPCode
from app.core.security import create_access_token

# CryptContext handles OTP hashing using bcrypt.
# We use the same hashing approach as passwords — even though this is an OTP,
# storing it as a hash means a database leak cannot be used to log in.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# How long an OTP is valid for
OTP_EXPIRY_MINUTES = 10

# How many digits the OTP has
OTP_LENGTH = 6


def _generate_otp() -> str:
    """
    Generates a cryptographically random 6-digit numeric OTP.

    We use random.SystemRandom() which uses the OS's secure random
    number generator (os.urandom), making it suitable for security tokens.
    """
    secure_random = random.SystemRandom()
    digits = string.digits  # "0123456789"
    return "".join(secure_random.choice(digits) for _ in range(OTP_LENGTH))


def _hash_otp(raw_otp: str) -> str:
    """
    Hashes the OTP using bcrypt before storing it in the database.
    The raw OTP is never persisted anywhere.
    """
    return pwd_context.hash(raw_otp)


def _verify_otp(raw_otp: str, hashed_otp: str) -> bool:
    """
    Verifies a raw OTP against its stored bcrypt hash.
    Returns True if they match, False otherwise.
    """
    return pwd_context.verify(raw_otp, hashed_otp)


def create_otp_for_email(email: str, db: Session) -> str:
    """
    Generates a new OTP for the given email address and stores it.

    Before creating a new OTP we invalidate all previous unused OTPs
    for this email. This prevents a user from having multiple valid
    OTPs in flight simultaneously, which would be a security risk.

    Returns the raw OTP string so the caller can send it via email.
    The raw OTP is NOT stored — only the hash is.
    """
    # Step 1 — Invalidate all existing unused OTPs for this email.
    # This means old OTPs stop working the moment a new one is requested.
    db.query(OTPCode).filter(
        OTPCode.email == email,
        OTPCode.is_used == False             # noqa: E712 (SQLAlchemy requires ==)
    ).update({"is_used": True})

    # Step 2 — Generate the raw OTP
    raw_otp = _generate_otp()

    # Step 3 — Compute the hash (we never store raw_otp)
    otp_hash = _hash_otp(raw_otp)

    # Step 4 — Compute the expiry timestamp
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    # Step 5 — Persist the hashed OTP
    otp_record = OTPCode(
        email=email,
        otp_hash=otp_hash,
        expires_at=expires_at,
        is_used=False,
    )
    db.add(otp_record)
    db.commit()

    # Step 6 — Return the raw OTP so it can be emailed.
    # After this point the raw OTP exists nowhere — only in the email.
    return raw_otp


def verify_otp_and_get_token(email: str, raw_otp: str, db: Session) -> str:
    """
    Verifies the OTP submitted by the user.

    Checks performed in order:
    1. A matching, unused, unexpired OTP record exists for this email
    2. The submitted OTP matches the stored hash
    3. Marks the OTP as used (prevents replay)
    4. Creates the user if they are new (first login = auto-registration)
    5. Returns a signed JWT

    Raises HTTP 400 for any invalid/expired/wrong OTP.
    We deliberately use a generic error message to prevent email enumeration
    (an attacker should not be able to tell which emails have accounts).
    """
    # Step 1 — Find the most recent unused, unexpired OTP for this email
    otp_record = db.query(OTPCode).filter(
        OTPCode.email == email,
        OTPCode.is_used == False,                       # must not be already used
        OTPCode.expires_at > datetime.utcnow()          # must not be expired
    ).order_by(OTPCode.created_at.desc()).first()       # most recent first

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code. Please request a new one."
        )

    # Step 2 — Verify the submitted raw OTP against the stored hash
    if not _verify_otp(raw_otp, otp_record.otp_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code. Please request a new one."
        )

    # Step 3 — Mark this OTP as used so it cannot be submitted again
    otp_record.is_used = True
    db.commit()

    # Step 4 — Create the user if this is their first login.
    # We use get_or_create logic: look up by email, create if not found.
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # First-time login — auto-register the user
        user = User(
            email=email,
            auth_provider="email_otp",
            auth_subject_id=email,   # for email OTP the email IS the subject ID
        )
        db.add(user)
        db.commit()
        db.refresh(user)             # loads the auto-generated id and timestamps

    # Step 5 — Issue a JWT and return it
    token = create_access_token(user_id=str(user.id))
    return token