# backend/app/core/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User

# HTTPBearer extracts the token from the Authorization: Bearer <token> header.
# auto_error=True means FastAPI returns 403 automatically if the header is missing.
bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency that validates the JWT and returns the current user.

    Usage in any route that requires authentication:
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}

    Raises HTTP 401 if:
    - No Authorization header is present
    - The token is invalid or expired
    - The user in the token no longer exists
    - The user account is deactivated
    """
    # Extract and decode the raw JWT string
    token = credentials.credentials
    payload = decode_access_token(token)

    # Get the user ID from the token's "sub" claim
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing user ID"
        )

    # Look up the user in the database
    # This ensures we catch deleted or deactivated users even if their
    # token hasn't expired yet
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    return user