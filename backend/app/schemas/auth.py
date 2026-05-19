# backend/app/schemas/auth.py

from pydantic import BaseModel, EmailStr

"""Schemas define the shape of request bodies and response payloads.
FastAPI uses them for automatic validation and serialisation."""

class RequestOTPSchema(BaseModel):
    """
    Request body for POST /auth/request-otp.
    The user submits only their email address.
    EmailStr validates that the value is a properly formatted email.
    """
    email: EmailStr


class VerifyOTPSchema(BaseModel):
    """
    Request body for POST /auth/verify-otp.
    The user submits their email and the 6-digit code from their inbox.
    """
    email: EmailStr
    otp: str                # The raw 6-digit code — e.g. "482917"


class TokenResponseSchema(BaseModel):
    """
    Response body returned after successful OTP verification.
    The frontend stores the access_token and sends it as a
    Bearer token on every subsequent request.
    """
    access_token: str
    token_type: str = "bearer"


class UserSchema(BaseModel):
    """
    Response body for GET /auth/me.
    We expose only safe, non-sensitive fields.
    """
    id: str
    email: str
    is_active: bool

    # This tells Pydantic to read data from SQLAlchemy model attributes,
    # not just from dictionaries.
    model_config = {"from_attributes": True}