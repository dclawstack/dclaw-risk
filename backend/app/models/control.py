from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from app.models.risk import Risk


class Control(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "controls"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    framework: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    control_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="preventive"
    )
    effectiveness: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)

    risks: Mapped[list["Risk"]] = relationship(
        secondary="risk_controls", back_populates="controls"
    )
