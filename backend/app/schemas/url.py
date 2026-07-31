from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl, computed_field, field_validator

from app.config import settings


class UrlCreate(BaseModel):
    """Request body schema for POST /api/urls."""

    original_url: HttpUrl
    custom_alias: str | None = None
    expires_at: datetime | None = None

    @field_validator("custom_alias", mode="before")
    @classmethod
    def validate_custom_alias(cls, v: str | None) -> str | None:
        if v is None:
            return None

        v = v.strip()

        if len(v) < 3 or len(v) > 50:
            raise ValueError("custom_alias must be between 3 and 50 characters.")

        import re
        if not re.match(r'^[a-zA-Z0-9\-]+$', v):
            raise ValueError(
                "custom_alias may only contain letters, digits, and hyphens."
            )

        return v


class UrlResponse(BaseModel):
    """Response schema for a single shortened URL."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    original_url: str
    short_code: str
    custom_alias: str | None
    created_at: datetime
    expires_at: datetime | None
    is_active: bool
    click_count: int

    @computed_field  # type: ignore[misc]
    @property
    def short_url(self) -> str:
        return f"{settings.BASE_DOMAIN}/{self.short_code}"


class UrlListResponse(BaseModel):
    """Paginated list of shortened URLs."""

    items: list[UrlResponse]
    total: int
    skip: int
    limit: int
