from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

from app.config import settings


class ClickRecord(BaseModel):
    """Represents a single click event."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    url_id: int
    clicked_at: datetime
    ip_address: str | None
    user_agent: str | None
    referrer: str | None


class UrlAnalyticsResponse(BaseModel):
    """Analytics data for a single shortened URL."""

    url_id: int
    short_code: str
    original_url: str
    total_clicks: int
    clicks: list[ClickRecord]


class TopUrl(BaseModel):
    """A top-performing URL for the summary endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    short_code: str
    original_url: str
    click_count: int

    @computed_field  # type: ignore[misc]
    @property
    def short_url(self) -> str:
        return f"{settings.BASE_DOMAIN}/{self.short_code}"


class AnalyticsSummary(BaseModel):
    """Aggregate analytics stats across all URLs."""

    total_links: int
    total_clicks: int
    top_urls: list[TopUrl]
