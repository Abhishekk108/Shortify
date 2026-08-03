"""
app/routers/urls.py — URL management endpoints (all require authentication).

Every operation is scoped to the authenticated user — users can only
see, create, and delete their own URLs.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session

from app.crud.url import (
    count_urls,
    create_url,
    delete_url,
    get_url_by_code,
    get_url_by_id,
    list_urls,
)
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.url import UrlCreate, UrlListResponse, UrlResponse
from app.services.shortener import get_unique_short_code
from app.services.validator import validate_url
from app.utils.rate_limit import limiter

router = APIRouter()


@router.post("", status_code=201, response_model=UrlResponse)
@limiter.limit("20/minute")
def create_short_url(
    payload: UrlCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a shortened URL owned by the authenticated user."""
    original_url_str = str(payload.original_url)

    try:
        cleaned_url = validate_url(original_url_str)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if payload.custom_alias:
        if get_url_by_code(db, payload.custom_alias) is not None:
            raise HTTPException(status_code=409, detail="Alias already in use")

    short_code = payload.custom_alias if payload.custom_alias else get_unique_short_code(db)

    return create_url(
        db,
        original_url=cleaned_url,
        short_code=short_code,
        user_id=current_user.id,
        custom_alias=payload.custom_alias,
        expires_at=payload.expires_at,
    )


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
