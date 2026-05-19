"""add P1/P2 tables: kris, incidents, scenarios, vendors, emerging_risks, culture_scores

Revision ID: 20260518_0002
Revises: 20260516_0001
Create Date: 2026-05-18
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260518_0002"
down_revision = "20260516_0001"
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
        "kris",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("unit", sa.String(32), nullable=False, server_default="count"),
        sa.Column("current_value", sa.Float, nullable=False, server_default="0"),
        sa.Column("threshold_warn", sa.Float, nullable=False),
        sa.Column("threshold_critical", sa.Float, nullable=False),
        sa.Column("direction", sa.String(8), nullable=False, server_default="above"),
        sa.Column(
            "risk_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("risks.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("owner", sa.String(255), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_kris_risk_id", "kris", ["risk_id"])

    op.create_table(
        "incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("severity", sa.Integer, nullable=False, server_default="3"),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "risk_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("risks.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(32), nullable=False, server_default="open"),
        *_timestamps(),
    )
    op.create_index("ix_incidents_risk_id", "incidents", ["risk_id"])

    op.create_table(
        "scenarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "multipliers",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        *_timestamps(),
    )

    op.create_table(
        "vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column("criticality", sa.Integer, nullable=False, server_default="3"),
        sa.Column("score", sa.Integer, nullable=False, server_default="50"),
        sa.Column("last_assessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ai_rationale", sa.Text, nullable=True),
        *_timestamps(),
    )

    op.create_table(
        "emerging_risks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("url", sa.Text, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("impact_score", sa.Integer, nullable=False, server_default="3"),
        sa.Column("status", sa.String(32), nullable=False, server_default="new"),
        *_timestamps(),
    )

    op.create_table(
        "culture_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("period", sa.String(16), nullable=False),
        sa.Column("dimension", sa.String(64), nullable=False),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("benchmark", sa.Integer, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        *_timestamps(),
    )


def downgrade() -> None:
    op.drop_table("culture_scores")
    op.drop_table("emerging_risks")
    op.drop_table("vendors")
    op.drop_table("scenarios")
    op.drop_index("ix_incidents_risk_id", table_name="incidents")
    op.drop_table("incidents")
    op.drop_index("ix_kris_risk_id", table_name="kris")
    op.drop_table("kris")
