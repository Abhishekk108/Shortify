"""
app/crud/url.py — Database access functions for the Url model.

All write operations (create, delete) are scoped to a specific user_id.
list_urls() filters by user_id so each user only sees their own links.
The redirect lookup (get_url_by_code) remains unscoped — it is intentionally
public so anyone visiting a short link is redirected correctly.
"""
from datetime import datetime

from sqlalchemy import func, update
from sqlalchemy.orm import Session

from app.models.click import Click
from app.models.url import Url


# ── Create ────────────────────────────────────────────────────────────────────

def create_url(
    db: Session,
    original_url: str,
    short_code: str,
    user_id: int | None = None,
    custom_alias: str | None = None,
    expires_at: datetime | None = None,
) -> Url:
    """
    Create and persist a new Url owned by *user_id*.

    Args:
        user_id: The id of the authenticated user creating this URL.
                 Stored as a FK so the URL is always scoped to its owner.
    """
    url = Url(
        original_url=original_url,
        short_code=short_code,
        custom_alias=custom_alias,
        expires_at=expires_at,
        user_id=user_id,
    )
    db.add(url)
    db.commit()
    db.refresh(url)
    return url


# ── Public lookup (used by the redirect endpoint — no user scoping) ──────────

def get_url_by_code(db: Session, code: str) -> Url | None:
    """
    Look up a URL by short_code first, then by custom_alias.
    Intentionally unscoped — any visitor can be redirected.
    """
    url = db.query(Url).filter(Url.short_code == code).first()
    if url is not None:
        return url
    return db.query(Url).filter(Url.custom_alias == code).first()


# ── Read (scoped to owner) ────────────────────────────────────────────────────

def get_url_by_id(db: Session, url_id: int, user_id: int | None = None) -> Url | None:
    """
    Fetch a Url by primary key.

    When *user_id* is provided, the lookup is scoped to that owner.
    Otherwise the function preserves the older unscoped behavior used by
    tests and non-authenticated lookup paths.
    """
    query = db.query(Url).filter(Url.id == url_id)
    if user_id is not None:
        query = query.filter(Url.user_id == user_id)
    return query.first()


def list_urls(
    db: Session,
    user_id: int | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Url]:
    """
    Return a paginated, newest-first list of URLs owned by *user_id*.

    If *search* is provided, filters where original_url, short_code, or
    custom_alias contain the term (case-insensitive).
    """
    query = db.query(Url)
    if user_id is not None:
        query = query.filter(Url.user_id == user_id)

    if search:
        pattern = f"%{search.lower()}%"
        query = query.filter(
            func.lower(Url.original_url).like(pattern)
            | func.lower(Url.short_code).like(pattern)
            | func.lower(Url.custom_alias).like(pattern)
        )

    return query.order_by(Url.created_at.desc()).offset(skip).limit(limit).all()


def count_urls(db: Session, user_id: int | None = None, search: str | None = None) -> int:
    """Return the total count of URLs, optionally filtered to the owner *user_id*."""
    query = db.query(func.count(Url.id))
    if user_id is not None:
        query = query.filter(Url.user_id == user_id)
    if search:
        pattern = f"%{search.lower()}%"
        query = query.filter(
            func.lower(Url.original_url).like(pattern)
            | func.lower(Url.short_code).like(pattern)
            | func.lower(Url.custom_alias).like(pattern)
        )
    return query.scalar() or 0


# ── Delete (scoped to owner) ──────────────────────────────────────────────────

def delete_url(db: Session, url_id: int, user_id: int | None = None) -> bool:
    """
    Delete the URL with *url_id* when it is either globally available or
    owned by *user_id*.

    A missing *user_id* preserves the older CRUD behavior used by tests.
    """
    query = db.query(Url).filter(Url.id == url_id)
    if user_id is not None:
        query = query.filter(Url.user_id == user_id)
    url = query.first()
    if url is None:
        return False
    db.delete(url)
    db.commit()
    return True


# ── Click helpers (unscoped — called by redirect endpoint) ───────────────────

def increment_click_count(db: Session, url_id: int) -> None:
    """Atomically increment click_count for the given URL id."""
    db.execute(
        update(Url)
        .where(Url.id == url_id)
        .values(click_count=Url.click_count + 1)
    )
    db.commit()


def create_click(
    db: Session,
    url_id: int,
    ip_address: str | None,
    user_agent: str | None,
    referrer: str | None,
) -> Click:
    """Create and persist a new Click record."""
    click = Click(
        url_id=url_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer,
    )
    db.add(click)
    db.commit()
    db.refresh(click)
    return click
