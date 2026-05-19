from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.risk import Risk


class Assessment(Base, UUIDPKMixin, TimestampMixin):
    """A point-in-time assessment of a risk.

    `kind = "qualitative"` records severity x probability scores.
    `kind = "quantitative"` records FAIR Monte Carlo loss percentiles.
    """

    __tablename__ = "assessments"

    risk_id: Mapped[UUID] = mapped_column(
        ForeignKey("risks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="qualitative")
    assessor: Mapped[str | None] = mapped_column(String(255), nullable=True)

    severity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    probability: Mapped[int | None] = mapped_column(Integer, nullable=True)

    loss_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    loss_mode: Mapped[float | None] = mapped_column(Float, nullable=True)
    loss_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    freq_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    freq_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    iterations: Mapped[int | None] = mapped_column(Integer, nullable=True)

    loss_p10: Mapped[float | None] = mapped_column(Float, nullable=True)
    loss_p50: Mapped[float | None] = mapped_column(Float, nullable=True)
    loss_p90: Mapped[float | None] = mapped_column(Float, nullable=True)
    loss_mean: Mapped[float | None] = mapped_column(Float, nullable=True)

    curve: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    risk: Mapped["Risk"] = relationship(back_populates="assessments")
