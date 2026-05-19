"""add risk-culture surveys + questions + responses

Revision ID: 20260518_0003
Revises: 20260518_0002
Create Date: 2026-05-18
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260518_0003"
down_revision = "20260518_0002"
branch_labels = None
depends_on = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "surveys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("period", sa.String(16), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        *_timestamps(),
    )

    op.create_table(
        "survey_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "survey_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("surveys.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("dimension", sa.String(64), nullable=False),
        sa.Column("prompt", sa.Text, nullable=False),
        sa.Column("order_index", sa.Integer, nullable=False, server_default="0"),
        *_timestamps(),
    )
    op.create_index(
        "ix_survey_questions_survey_id", "survey_questions", ["survey_id"]
    )

    op.create_table(
        "survey_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "survey_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("surveys.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("survey_questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("respondent_hash", sa.String(64), nullable=True),
        sa.Column("score", sa.Integer, nullable=False),
        *_timestamps(),
    )
    op.create_index(
        "ix_survey_responses_survey_id", "survey_responses", ["survey_id"]
    )
    op.create_index(
        "ix_survey_responses_question_id", "survey_responses", ["question_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_survey_responses_question_id", table_name="survey_responses"
    )
    op.drop_index("ix_survey_responses_survey_id", table_name="survey_responses")
    op.drop_table("survey_responses")
    op.drop_index(
        "ix_survey_questions_survey_id", table_name="survey_questions"
    )
    op.drop_table("survey_questions")
    op.drop_table("surveys")
