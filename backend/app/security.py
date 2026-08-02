"""
app/security.py — Password hashing helpers.

Uses passlib with the bcrypt scheme.  All password operations in the
application go through this module so the hashing algorithm is configured
in exactly one place.

Usage:
    from app.security import hash_password, verify_password

    hashed = hash_password("mysecretpassword")
    ok     = verify_password("mysecretpassword", hashed)   # True
    bad    = verify_password("wrongpassword",    hashed)   # False
"""
from passlib.context import CryptContext

# Single CryptContext instance — bcrypt is the active (and only) scheme.
# deprecated="auto" means passlib will transparently upgrade old hashes
# if we ever add a stronger scheme in the future.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Returns a bcrypt hash string suitable for storage.
    Never store or log the plain-text password after this call.
    """
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    Returns True if the password matches, False otherwise.
    Constant-time comparison — safe against timing attacks.
    """
    return _pwd_context.verify(plain_password, hashed_password)
