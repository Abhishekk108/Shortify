from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url_id: Mapped[int] = mapped_column(Integer, ForeignKey("urls.id"), nullable=False, index=True)
    clicked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    # 45 chars to support both IPv4 and IPv6 addresses
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    referrer: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    # Many-to-one: many clicks belong to one URL
    url: Mapped["Url"] = relationship("Url", back_populates="clicks")

    def __repr__(self) -> str:
        return f"<Click id={self.id} url_id={self.url_id} clicked_at={self.clicked_at}>"
