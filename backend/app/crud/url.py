from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.click import Click
from app.models.url import Url


def create_url(
    db: Session,
    original_url: str,
    short_code: str,
    custom_alias: str | None = None,
    expires_at: datetime | None = None,
) -> Url:
    """Create and persist a new Url record. Returns the created object."""
    url = Url(
        original_url=original_url,
        short_code=short_code,
        custom_alias=custom_alias,
        expires_at=expires_at,
    )
    db.add(url)
    db.commit()
    db.refresh(url)
    return url


def get_url_by_code(db: Session, code: str) -> Url | None:
    """
    Look up a URL by short_code first, then by custom_alias.
    Returns the first match or None.
    """
    url = db.query(Url).filter(Url.short_code == code).first()
    if url is not None:
        return url
    return db.query(Url).filter(Url.custom_alias == code).first()


def get_url_by_id(db: Session, url_id: int) -> Url | None:
    """Fetch a Url by primary key. Returns the Url or None."""
    return db.query(Url).filter(Url.id == url_id).first()


def list_urls(
    db: Session,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Url]:
    """
    Return a paginated, newest-first list of URLs.

    If *search* is provided, filters rows where original_url, short_code, or
    custom_alias contain the search term (case-insensitive via func.lower()).
    """
    query = db.query(Url)

    if search:
        pattern = f"%{search.lower()}%"
        query = query.filter(
            func.lower(Url.original_url).like(pattern)
            | func.lower(Url.short_code).like(pattern)
            | func.lower(Url.custom_alias).like(pattern)
        )

    return query.order_by(Url.created_at.desc()).offset(skip).limit(limit).all()


def delete_url(db: Session, url_id: int) -> bool:
    """
    Delete the Url with the given id (cascade removes associated clicks).
    Returns True if a row was deleted, False if not found.
    """
    url = db.query(Url).filter(Url.id == url_id).first()
    if url is None:
        return False
    db.delete(url)
    db.commit()
    return True


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
    """Create and persist a new Click record. Returns the created object."""
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
