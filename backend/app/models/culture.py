"""P2.2 Risk Culture — survey-response model.

The survey UX (question library, employee assignment, anonymity controls) is
not built yet. This module persists already-collected scores so a dashboard
can render the org-wide trend immediately.
"""

from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class CultureScore(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "culture_scores"

    period: Mapped[str] = mapped_column(String(16), nullable=False)  # e.g. "2026-Q2"
    dimension: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # e.g. "Speak-up", "Tone-at-top"
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-100
    benchmark: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
