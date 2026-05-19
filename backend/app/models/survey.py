from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class Survey(Base, UUIDPKMixin, TimestampMixin):
    """A risk-culture survey targeting one or more dimensions."""

    __tablename__ = "surveys"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    period: Mapped[str] = mapped_column(String(16), nullable=False)  # 2026-Q2
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="draft"
    )  # draft | open | closed

    questions: Mapped[list["SurveyQuestion"]] = relationship(
        back_populates="survey", cascade="all, delete-orphan"
    )
    responses: Mapped[list["SurveyResponse"]] = relationship(
        back_populates="survey", cascade="all, delete-orphan"
    )


class SurveyQuestion(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "survey_questions"

    survey_id: Mapped[UUID] = mapped_column(
        ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dimension: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    survey: Mapped["Survey"] = relationship(back_populates="questions")


class SurveyResponse(Base, UUIDPKMixin, TimestampMixin):
    """A single 0-100 answer to a single question from a (typically anonymous) respondent."""

    __tablename__ = "survey_responses"

    survey_id: Mapped[UUID] = mapped_column(
        ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id: Mapped[UUID] = mapped_column(
        ForeignKey("survey_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    respondent_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )  # opaque token, no PII
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100

    survey: Mapped["Survey"] = relationship(back_populates="responses")
