"""initial schema: risks, controls, risk_controls, assessments

Revision ID: 20260516_0001
Revises:
Create Date: 2026-05-16
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260516_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "risks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="identified"),
        sa.Column("owner", sa.String(255), nullable=True),
        sa.Column("severity", sa.Integer, nullable=False, server_default="3"),
        sa.Column("probability", sa.Integer, nullable=False, server_default="3"),
        sa.Column("velocity", sa.Integer, nullable=False, server_default="3"),
        sa.Column("ai_classification", sa.String(64), nullable=True),
        sa.Column("ai_rationale", sa.Text, nullable=True),
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
    )
    op.create_index("ix_risks_category", "risks", ["category"])
    op.create_index("ix_risks_status", "risks", ["status"])

    op.create_table(
        "controls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("framework", sa.String(64), nullable=True),
        sa.Column(
            "control_type", sa.String(32), nullable=False, server_default="preventive"
        ),
        sa.Column("effectiveness", sa.Integer, nullable=False, server_default="3"),
        sa.Column("owner", sa.String(255), nullable=True),
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
    )
    op.create_index("ix_controls_framework", "controls", ["framework"])

    op.create_table(
        "risk_controls",
        sa.Column(
            "risk_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("risks.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "control_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("controls.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("effectiveness", sa.Integer, nullable=False, server_default="3"),
        sa.UniqueConstraint("risk_id", "control_id", name="uq_risk_control"),
    )

    op.create_table(
        "assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "risk_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("risks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "kind", sa.String(32), nullable=False, server_default="qualitative"
        ),
        sa.Column("assessor", sa.String(255), nullable=True),
        sa.Column("severity", sa.Integer, nullable=True),
        sa.Column("probability", sa.Integer, nullable=True),
        sa.Column("loss_min", sa.Float, nullable=True),
        sa.Column("loss_mode", sa.Float, nullable=True),
        sa.Column("loss_max", sa.Float, nullable=True),
        sa.Column("freq_min", sa.Float, nullable=True),
        sa.Column("freq_max", sa.Float, nullable=True),
        sa.Column("iterations", sa.Integer, nullable=True),
        sa.Column("loss_p10", sa.Float, nullable=True),
        sa.Column("loss_p50", sa.Float, nullable=True),
        sa.Column("loss_p90", sa.Float, nullable=True),
        sa.Column("loss_mean", sa.Float, nullable=True),
        sa.Column("curve", postgresql.JSONB, nullable=True),
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
    )
    op.create_index("ix_assessments_risk_id", "assessments", ["risk_id"])


def downgrade() -> None:
    op.drop_index("ix_assessments_risk_id", table_name="assessments")
    op.drop_table("assessments")
    op.drop_table("risk_controls")
    op.drop_index("ix_controls_framework", table_name="controls")
    op.drop_table("controls")
    op.drop_index("ix_risks_status", table_name="risks")
    op.drop_index("ix_risks_category", table_name="risks")
    op.drop_table("risks")
