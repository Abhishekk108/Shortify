"""
app/routers/urls.py — URL management endpoints.

POST /api/urls  — public (guests allowed, 3/day limit) OR authenticated (unlimited)
GET/DELETE      — authenticated only, scoped to the current user
"""
import uuid

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session

from app.crud.url import (
    count_guest_urls_today,
    count_urls,
    create_url,
    delete_url,
    get_url_by_code,
    get_url_by_id,
    list_urls,
)
from app.database import get_db
from app.dependencies.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.schemas.url import UrlCreate, UrlListResponse, UrlResponse
from app.services.shortener import get_unique_short_code
from app.services.validator import validate_url
from app.utils.rate_limit import limiter

router = APIRouter()

GUEST_DAILY_LIMIT = 3
GUEST_COOKIE_NAME = "shortify_guest_id"
GUEST_LIMIT_MESSAGE = (
    "Guest limit reached. Create a free account for unlimited link creation and analytics."
)


@router.post("", status_code=201, response_model=UrlResponse)
@limiter.limit("100/minute")
def create_short_url(
    payload: UrlCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
    # Read existing guest_id cookie (None if first visit or logged in)
    shortify_guest_id: str | None = Cookie(default=None),
):
    """
    Create a shortened URL.

    - Authenticated users: unlimited, URL is owned by the user.
    - Guests: max 3 links per calendar day (UTC), identified by a UUID cookie.
    """
    # ── Validate the target URL ───────────────────────────────────────────────
    try:
        cleaned_url = validate_url(str(payload.original_url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # ── Custom alias collision check ──────────────────────────────────────────
    if payload.custom_alias:
        if get_url_by_code(db, payload.custom_alias) is not None:
            raise HTTPException(status_code=409, detail="Alias already in use")

    short_code = payload.custom_alias if payload.custom_alias else get_unique_short_code(db)

    # ── Authenticated path ────────────────────────────────────────────────────
    if current_user is not None:
        url = create_url(
            db,
            original_url=cleaned_url,
            short_code=short_code,
            user_id=current_user.id,
            custom_alias=payload.custom_alias,
            expires_at=payload.expires_at,
        )
        return url

    # ── Guest path ─────────────────────────────────────────────────────────────
    # Resolve or mint the guest_id
    guest_id = shortify_guest_id
    is_new_guest = guest_id is None
    if is_new_guest:
        guest_id = str(uuid.uuid4())

    # Enforce daily limit
    if count_guest_urls_today(db, guest_id) >= GUEST_DAILY_LIMIT:
        raise HTTPException(status_code=429, detail=GUEST_LIMIT_MESSAGE)

    url = create_url(
        db,
        original_url=cleaned_url,
        short_code=short_code,
        guest_id=guest_id,
        custom_alias=payload.custom_alias,
        expires_at=payload.expires_at,
    )

    # Set the cookie on the response (1 year, httponly, samesite=lax)
    response.set_cookie(
        key=GUEST_COOKIE_NAME,
        value=guest_id,
        max_age=365 * 24 * 60 * 60,
        httponly=True,
        samesite="lax",
        secure=False,   # set True in production behind HTTPS
    )
    return url


@router.get("", status_code=200, response_model=UrlListResponse)
def get_urls(
    search: str | None = None,
    skip: int = 0,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the authenticated user's URLs with optional search and pagination."""
    urls = list_urls(db, user_id=current_user.id, search=search, skip=skip, limit=limit)
    total = count_urls(db, user_id=current_user.id, search=search)
    return UrlListResponse(items=urls, total=total, skip=skip, limit=limit)


@router.get("/{id}", status_code=200, response_model=UrlResponse)
def get_url(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single URL by ID — only if it belongs to the authenticated user."""
    url = get_url_by_id(db, url_id=id, user_id=current_user.id)
    if url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return url


@router.delete("/{id}", status_code=204)
def remove_url(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a URL by ID — only if it belongs to the authenticated user."""
    if not delete_url(db, url_id=id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="URL not found")
    return Response(status_code=204)
