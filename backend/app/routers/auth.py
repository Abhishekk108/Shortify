"""
app/routers/auth.py — Authentication endpoints.

POST /api/auth/register  — create a new user account
POST /api/auth/login     — verify credentials, return a JWT access token
GET  /api/auth/me        — return the currently authenticated user
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import (
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.security import verify_password
from app.utils.jwt import create_access_token

router = APIRouter()


# ── POST /api/auth/register ───────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Create a new user account.

    - Validates that the email and username are not already taken.
    - Hashes the password before storing (plain text is never persisted).
    - Returns the created user without exposing the hashed password.
    """
    # ── Uniqueness checks ─────────────────────────────────────────────────────
    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )

    if get_user_by_username(db, payload.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists.",
        )

    # ── Persist (hashing happens inside create_user) ──────────────────────────
    user = create_user(db, payload)
    return user


# ── POST /api/auth/login ──────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Log in and receive a JWT access token",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """
    Authenticate a user by email or username + password.

    - The `identifier` field accepts either an email address or a username.
    - Returns a JWT access token on success.
    - Always returns HTTP 401 on failure — the error message intentionally does
      not reveal whether the identifier or the password was wrong (prevents
      user enumeration).
    """
    _INVALID = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # ── Look up user by email first, then by username ─────────────────────────
    user = get_user_by_email(db, payload.identifier)
    if user is None:
        user = get_user_by_username(db, payload.identifier)
    if user is None:
        raise _INVALID

    # ── Verify password ───────────────────────────────────────────────────────
    if not verify_password(payload.password, user.hashed_password):
        raise _INVALID

    # ── Issue JWT token ───────────────────────────────────────────────────────
    # Subject claim ("sub") stores the user's email — stable, unique identifier.
    access_token = create_access_token(data={"sub": user.email})

    return Token(access_token=access_token, token_type="bearer")


# ── GET /api/auth/me ──────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the currently authenticated user",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    Return the profile of the authenticated user.

    Requires: Bearer token in Authorization header.
    Returns the same shape as /register — id, username, email, created_at.
    """
    return current_user
