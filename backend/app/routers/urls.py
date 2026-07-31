from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.url import (
    create_url,
    delete_url,
    get_url_by_code,
    get_url_by_id,
    list_urls,
)
from app.database import get_db
from app.models.url import Url
from app.schemas.url import UrlCreate, UrlListResponse, UrlResponse
from app.services.shortener import get_unique_short_code
from app.services.validator import validate_url

router = APIRouter()


@router.post("", status_code=201, response_model=UrlResponse)
def create_short_url(payload: UrlCreate, db: Session = Depends(get_db)):
    """Create a new shortened URL."""
    # Convert Pydantic HttpUrl to plain string
    original_url_str = str(payload.original_url)

    # Validate the URL
    try:
        cleaned_url = validate_url(original_url_str)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Check for custom alias collision
    if payload.custom_alias:
        existing = get_url_by_code(db, payload.custom_alias)
        if existing is not None:
            raise HTTPException(status_code=409, detail="Alias already in use")

    # Determine short code
    short_code = payload.custom_alias if payload.custom_alias else get_unique_short_code(db)

    # Persist
    url = create_url(
        db,
        original_url=cleaned_url,
        short_code=short_code,
        custom_alias=payload.custom_alias,
        expires_at=payload.expires_at,
    )
    return url


@router.get("", status_code=200, response_model=UrlListResponse)
def get_urls(
    search: str | None = None,
    skip: int = 0,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """List URLs with optional search and pagination."""
    urls = list_urls(db, search=search, skip=skip, limit=limit)

    # Count query with the same search filter
    count_query = db.query(func.count(Url.id))
    if search:
        pattern = f"%{search.lower()}%"
        count_query = count_query.filter(
            func.lower(Url.original_url).like(pattern)
            | func.lower(Url.short_code).like(pattern)
            | func.lower(Url.custom_alias).like(pattern)
        )
    total = count_query.scalar() or 0

    return UrlListResponse(items=urls, total=total, skip=skip, limit=limit)


@router.get("/{id}", status_code=200, response_model=UrlResponse)
def get_url(id: int, db: Session = Depends(get_db)):
    """Get a single URL by ID."""
    url = get_url_by_id(db, id)
    if url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return url


@router.delete("/{id}", status_code=204)
def remove_url(id: int, db: Session = Depends(get_db)):
    """Delete a URL by ID."""
    deleted = delete_url(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="URL not found")
    return Response(status_code=204)
