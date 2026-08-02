"""
app/utils/jwt.py — JWT creation and verification.

Uses python-jose with the HS256 algorithm.
SECRET_KEY and ALGORITHM come from app.config.settings so there is
a single source of truth — never hard-code them here.
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


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT string to decode.

    Returns:
        The decoded payload dict.

    Raises:
        jose.JWTError: If the token is expired, tampered with, or otherwise invalid.
                       Callers are responsible for catching this and returning 401.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
