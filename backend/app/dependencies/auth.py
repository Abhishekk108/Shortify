"""
app/dependencies/auth.py — FastAPI authentication dependencies.

Provides two reusable Depends()-able functions:

    get_current_user()          → User   (required — raises 401 if unauthenticated)
    get_current_user_optional() → User | None  (returns None for anonymous requests)

Usage in a router:
    from app.dependencies.auth import get_current_user
    from app.models.user import User

    @router.get("/protected")
    def my_route(current_user: User = Depends(get_current_user)):
        ...

Token format expected in the Authorization header:
    Authorization: Bearer <jwt_token>
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.crud.user import get_user_by_email
from app.database import get_db
from app.models.user import User
from app.utils.jwt import verify_access_token

# OAuth2PasswordBearer extracts the Bearer token from the Authorization header.
# tokenUrl points to the login endpoint so Swagger UI can populate it.
# auto_error=False is used only in the optional variant — the required variant
# uses auto_error=True (the default) so FastAPI returns 401 automatically when
# the header is absent entirely.
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
_oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False,   # returns None instead of raising 401 when header missing
)


# ── Required authentication ───────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(_oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency — extract and validate the Bearer token, return the User.

    Steps:
      1. FastAPI (via OAuth2PasswordBearer) extracts the token from
         "Authorization: Bearer <token>". If the header is absent, returns 401.
      2. verify_access_token() validates the signature and expiry, returns "sub".
      3. The user is looked up in the database by email (the "sub" value).
      4. If any step fails the caller receives HTTP 401 Unauthorized.

    Returns:
        The authenticated User ORM object.

    Raises:
        HTTPException 401: On missing header, invalid/expired token, or
                           if the user no longer exists in the database.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        email = verify_access_token(token)
    except JWTError:
        raise credentials_error

    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_error

    return user


# ── Optional authentication ───────────────────────────────────────────────────

def get_current_user_optional(
    token: str | None = Depends(_oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> User | None:
    """
    FastAPI dependency — same as get_current_user but returns None for
    anonymous (unauthenticated) requests instead of raising 401.

    Use this on routes that behave differently for authenticated vs
    anonymous users but must remain publicly accessible (e.g. POST /api/urls
    which can be used without login but will associate the URL with a user
    when a valid token is provided).

    Returns:
        The authenticated User, or None for anonymous requests.
    """
    if token is None:
        return None

    try:
        email = verify_access_token(token)
    except JWTError:
        return None

    return get_user_by_email(db, email)
