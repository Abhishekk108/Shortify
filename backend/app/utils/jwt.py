"""
app/utils/jwt.py — JWT creation and verification.

Uses python-jose with the HS256 algorithm.
SECRET_KEY and ALGORITHM come from app.config.settings so there is
a single source of truth — never hard-code them here.

Public API
----------
create_access_token(data, expires_delta)  → str
verify_access_token(token)                → str   (returns the "sub" claim)
decode_access_token(token)                → dict  (returns full payload)
"""
from datetime import datetime, timedelta

from jose import JWTError, jwt

from app.config import settings


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Encode a JWT access token.

    Args:
        data:          Payload dict. Must include a "sub" key (subject = user identity).
        expires_delta: How long the token is valid. Defaults to
                       settings.ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        A signed JWT string.
    """
    payload = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload["exp"] = expire
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str) -> str:
    """
    Verify a JWT access token and return the subject claim ("sub").

    This is the primary function for authentication checks — it validates
    the signature, checks expiry, and extracts the user identity in one call.

    Args:
        token: The raw JWT string (without "Bearer " prefix).

    Returns:
        The value of the "sub" claim (typically the user's email).

    Raises:
        jose.JWTError: If the token is expired, has an invalid signature,
                       is structurally malformed, or has no "sub" claim.
                       Callers should map this to HTTP 401.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    subject: str | None = payload.get("sub")
    if subject is None:
        raise JWTError("Token payload is missing the 'sub' claim.")
    return subject


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token, returning the full payload.

    Use this when you need claims beyond "sub" (e.g. roles, scopes).
    For simple authentication, prefer verify_access_token().

    Args:
        token: The JWT string to decode.

    Returns:
        The decoded payload dict.

    Raises:
        jose.JWTError: On any validation failure.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
