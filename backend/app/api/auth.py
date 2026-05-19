# backend/app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.core.mail import send_otp_email
from app.schemas.auth import RequestOTPSchema, VerifyOTPSchema, TokenResponseSchema, UserSchema
from app.services.auth_service import create_otp_for_email, verify_otp_and_get_token
from app.models.user import User

# All routes in this file are prefixed with /auth.
# The tag "auth" groups them together in the Swagger docs at /docs.
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/request-otp",
    status_code=status.HTTP_200_OK,
    summary="Request a one-time password via email"
)
async def request_otp(
    body: RequestOTPSchema,
    background_tasks: BackgroundTasks,      # FastAPI's built-in background task runner
    db: Session = Depends(get_db)
):
    """
    Step 1 of the login flow.

    The user submits their email. We generate an OTP, store the hash,
    and send the raw OTP to their inbox.

    We use BackgroundTasks to send the email asynchronously.
    This means the HTTP response is returned immediately (within milliseconds)
    while the email sends in the background. The user sees a fast response
    and the email arrives shortly after.

    We always return the same success message regardless of whether the
    email address has an account. This prevents an attacker from using
    this endpoint to discover which emails are registered (enumeration attack).
    """
    # Generate and store the OTP in the database
    raw_otp = create_otp_for_email(email=body.email, db=db)

    # Schedule the email to send after this response is returned.
    # send_otp_email is an async function — BackgroundTasks handles that correctly.
    background_tasks.add_task(send_otp_email, email=body.email, otp=raw_otp)

    # Always return a generic success message
    return {
        "message": "If an account exists for this email, a login code has been sent."
    }


@router.post(
    "/verify-otp",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Verify the OTP and receive a JWT"
)
def verify_otp(
    body: VerifyOTPSchema,
    db: Session = Depends(get_db)
):
    """
    Step 2 of the login flow.

    The user submits their email and the 6-digit OTP from their inbox.
    We verify the OTP and return a signed JWT.

    On first login, the user is automatically registered — no separate
    registration step is needed.
    """
    # The service handles all verification logic and raises HTTPException
    # with appropriate messages on failure
    token = verify_otp_and_get_token(
        email=body.email,
        raw_otp=body.otp,
        db=db
    )

    return TokenResponseSchema(access_token=token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Get the current authenticated user"
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the profile of the currently authenticated user.

    The get_current_user dependency validates the JWT from the
    Authorization: Bearer <token> header and returns the User model.
    This endpoint requires a valid token — it returns 401 if missing or invalid.
    """
    return current_user