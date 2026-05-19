from __future__ import annotations

from uuid import UUID

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class KRI(Base, UUIDPKMixin, TimestampMixin):
    """Key Risk Indicator: a metric watched against warn/critical thresholds.

    Optionally tied to a specific risk in the register so breaches surface
    on the risk's detail page.
    """

    __tablename__ = "kris"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(String(32), nullable=False, default="count")
    current_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    threshold_warn: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_critical: Mapped[float] = mapped_column(Float, nullable=False)
    direction: Mapped[str] = mapped_column(
        String(8), nullable=False, default="above"
    )  # "above" or "below" — which side of threshold is bad
    risk_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("risks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)

    @property
    def status(self) -> str:
        if self.direction == "above":
            if self.current_value >= self.threshold_critical:
                return "critical"
            if self.current_value >= self.threshold_warn:
                return "warn"
            return "ok"
        # direction == "below" — lower is worse (e.g. patch-coverage %)
        if self.current_value <= self.threshold_critical:
            return "critical"
        if self.current_value <= self.threshold_warn:
            return "warn"
        return "ok"
