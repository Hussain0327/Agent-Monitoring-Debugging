"""Initial schema: traces, spans, projects, api_keys, drift_alerts.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Projects
    op.create_table(
        "projects",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("description", sa.String(1024), server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # API Keys
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(64),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("key", sa.String(256), unique=True, nullable=False),
        sa.Column("name", sa.String(128), server_default="default"),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_api_keys_project_id", "api_keys", ["project_id"])

    # Traces
    op.create_table(
        "traces",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(256), server_default=""),
        sa.Column("status", sa.String(32), server_default="unset"),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_traces_project_id", "traces", ["project_id"])

    # Spans
    op.create_table(
        "spans",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "trace_id",
            sa.String(64),
            sa.ForeignKey("traces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("parent_span_id", sa.String(64), nullable=True),
        sa.Column("name", sa.String(256), server_default=""),
        sa.Column("kind", sa.String(32), server_default="custom"),
        sa.Column("status", sa.String(32), server_default="unset"),
        sa.Column("input", sa.JSON, nullable=True),
        sa.Column("output", sa.JSON, nullable=True),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("events", sa.JSON, nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_spans_trace_id", "spans", ["trace_id"])
    op.create_index("ix_spans_parent_span_id", "spans", ["parent_span_id"])

    # Drift Alerts
    op.create_table(
        "drift_alerts",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("span_kind", sa.String(32), nullable=False),
        sa.Column("metric_name", sa.String(128), nullable=False),
        sa.Column("baseline_value", sa.Float, nullable=False),
        sa.Column("current_value", sa.Float, nullable=False),
        sa.Column("psi_score", sa.Float, nullable=False),
        sa.Column("severity", sa.String(32), server_default="low"),
        sa.Column("resolved", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_drift_alerts_project_id", "drift_alerts", ["project_id"])


def downgrade() -> None:
    op.drop_table("drift_alerts")
    op.drop_table("spans")
    op.drop_table("traces")
    op.drop_table("api_keys")
    op.drop_table("projects")
