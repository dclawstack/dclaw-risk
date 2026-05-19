from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class Scenario(Base, UUIDPKMixin, TimestampMixin):
    """A what-if scenario with per-category severity/probability multipliers.

    Example: a 'severe recession' scenario might be
        {"Financial": {"severity": 1.5, "probability": 1.3},
         "Operational": {"severity": 1.2, "probability": 1.0}}
    """

    __tablename__ = "scenarios"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    multipliers: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
