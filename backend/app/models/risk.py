from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.assessment import Assessment
    from app.models.control import Control


class Risk(Base, UUIDPKMixin, TimestampMixin):
    """A risk in the register.

    Severity / probability are 1-5 qualitative scores. Quantitative loss
    estimates live on Assessment rows so a risk can be re-assessed over time.
    """

    __tablename__ = "risks"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="identified", index=True
    )
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)

    severity: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    probability: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    velocity: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    ai_classification: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ai_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="risk", cascade="all, delete-orphan"
    )
    controls: Mapped[list["Control"]] = relationship(
        secondary="risk_controls", back_populates="risks"
    )

    @property
    def score(self) -> int:
        return self.severity * self.probability


class RiskControl(Base):
    """M2M between risks and controls with per-link effectiveness score."""

    __tablename__ = "risk_controls"
    __table_args__ = (UniqueConstraint("risk_id", "control_id", name="uq_risk_control"),)

    risk_id: Mapped[UUID] = mapped_column(
        ForeignKey("risks.id", ondelete="CASCADE"), primary_key=True
    )
    control_id: Mapped[UUID] = mapped_column(
        ForeignKey("controls.id", ondelete="CASCADE"), primary_key=True
    )
    effectiveness: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
