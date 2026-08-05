from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    original_url: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    custom_alias: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Owner — nullable (pre-auth URLs have no owner)
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Guest identifier — UUID set via cookie for unauthenticated visitors
    guest_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    # Relationships
    owner: Mapped["User | None"] = relationship("User", back_populates="urls")  # type: ignore[name-defined]

    clicks: Mapped[list["Click"]] = relationship(  # type: ignore[name-defined]
        "Click",
        back_populates="url",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Url id={self.id} short_code={self.short_code!r} user_id={self.user_id}>"
