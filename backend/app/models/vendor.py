from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class Vendor(Base, UUIDPKMixin, TimestampMixin):
    """A third-party vendor we depend on, with a risk score 1-100."""

    __tablename__ = "vendors"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    criticality: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    last_assessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ai_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
