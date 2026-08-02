"""
Pydantic schemas for User registration and responses.
Authentication (login/tokens) is handled separately — not included here.
"""
import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


# ── Request schema ────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Payload for creating a new user account."""

    username: str
    email: EmailStr
    password: str

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if len(v) > 50:
            raise ValueError("Username must be 50 characters or fewer.")
        if not re.match(r"^[a-zA-Z0-9_\-]+$", v):
            raise ValueError(
                "Username may only contain letters, digits, underscores, and hyphens."
            )
        return v

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


# ── Response schema ───────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    """Public representation of a user — never exposes hashed_password."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime
