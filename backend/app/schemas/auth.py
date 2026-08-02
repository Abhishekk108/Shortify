"""
Pydantic schemas for authentication requests and token responses.
"""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """
    Accepted login credentials.
    Supports both email and username — the router checks both.
    """
    identifier: str  # email address OR username
    password: str


class Token(BaseModel):
    """Response returned after a successful login."""
    access_token: str
    token_type: str = "bearer"
