from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.crud.url import create_click, get_url_by_code, increment_click_count
from app.database import get_db
from app.utils.rate_limit import limiter

router = APIRouter()


@router.get("/{short_code}", tags=["Redirect"])
@limiter.limit("60/minute")
def redirect_to_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    """Look up a short code, log the click, and redirect to the original URL.

    Rate limited to 60 requests/minute per IP address.
    Returns:
        307 Temporary Redirect on success
        404 if short code not found
        410 if link is inactive or expired
        429 if rate limit exceeded
    """
    url = get_url_by_code(db, short_code)

    if url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    if not url.is_active:
        raise HTTPException(status_code=410, detail="This link has been deactivated")

    if url.expires_at is not None and url.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="This link has expired")

    # Extract request metadata for click logging
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")

    # Log click then atomically increment counter
    create_click(db, url_id=url.id, ip_address=ip_address, user_agent=user_agent, referrer=referrer)
    increment_click_count(db, url.id)

    return RedirectResponse(url=url.original_url, status_code=307)
