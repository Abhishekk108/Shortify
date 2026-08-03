"""
app/routers/analytics.py — Analytics endpoints (require authentication).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.url import get_url_by_id
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.click import Click
from app.models.url import Url
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary, UrlAnalyticsResponse

router = APIRouter()


@router.get("/urls/{id}/analytics", status_code=200, response_model=UrlAnalyticsResponse)
def get_url_analytics(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return full click history and stats for a single URL.

    Requires: Bearer token in Authorization header.
    """
    url = get_url_by_id(db, id)
    if url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    clicks = (
        db.query(Click)
        .filter(Click.url_id == id)
        .order_by(Click.clicked_at.desc())
        .all()
    )

    return UrlAnalyticsResponse(
        url_id=url.id,
        short_code=url.short_code,
        original_url=url.original_url,
        total_clicks=url.click_count,
        clicks=clicks,
    )


@router.get("/analytics/summary", status_code=200, response_model=AnalyticsSummary)
def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return aggregate stats: total links, total clicks, and top 5 URLs.

    Requires: Bearer token in Authorization header.
    """
    total_links = db.query(func.count(Url.id)).scalar() or 0
    total_clicks = db.query(func.sum(Url.click_count)).scalar() or 0
    top_urls = db.query(Url).order_by(Url.click_count.desc()).limit(5).all()

    return AnalyticsSummary(
        total_links=total_links,
        total_clicks=total_clicks,
        top_urls=top_urls,
    )
