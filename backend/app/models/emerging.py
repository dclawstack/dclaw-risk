"""P2.1 Emerging Risk — model for risks surfaced from external sources.

The pipeline that ingests feeds (RSS, threat intel, regulator publications)
is not wired up yet — see app/services/emerging.py for the placeholder.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class EmergingRisk(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "emerging_risks"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    impact_score: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="new"
    )  # new | reviewed | promoted (to risk register)
