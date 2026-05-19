# backend/app/core/security.py

import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status

# Read JWT config from environment variables.
# These must be set in your .env file locally and in Railway variables
# for production.
SECRET_KEY = os.environ.get("JWT_SECRET")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", 60))

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET environment variable is not set")


def create_access_token(user_id: str) -> str:
    """
    Creates a signed JWT containing the user's ID.

    The token payload contains:
    - sub: the user's UUID as a string (industry standard claim name for subject)
    - exp: the expiry timestamp (handled automatically by python-jose)

    The token is signed with the SECRET_KEY using HS256.
    Anyone who has this token can act as the user until it expires,
    so keep SECRET_KEY secret and use HTTPS in production.
    """
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),    # subject — the user's UUID
        "exp": expire,           # expiry — python-jose validates this on decode
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodes and validates a JWT.

    Raises HTTP 401 if:
    - The token signature is invalid (tampered token)
    - The token has expired
    - The token is malformed

    Returns the decoded payload dict on success.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )