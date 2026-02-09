"""Add project_settings and notifications tables, extend replay_runs.

Revision ID: 005
Revises: 004
Create Date: 2024-07-01 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- project_settings ---
    op.create_table(
        "project_settings",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("openai_api_key_encrypted", sa.String(length=512), nullable=True),
        sa.Column("anthropic_api_key_encrypted", sa.String(length=512), nullable=True),
        sa.Column("default_openai_model", sa.String(length=128), nullable=False, server_default="gpt-4o"),
        sa.Column("default_anthropic_model", sa.String(length=128), nullable=False, server_default="claude-sonnet-4-5-20250929"),
        sa.Column("drift_check_interval_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("drift_check_enabled", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index("ix_project_settings_project_id", "project_settings", ["project_id"])

    # --- notifications ---
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column("reference_id", sa.String(length=64), nullable=True),
        sa.Column("read", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_project_id", "notifications", ["project_id"])
    op.create_index("ix_notifications_read", "notifications", ["read"])

    # --- extend replay_runs with new columns ---
    op.add_column("replay_runs", sa.Column("estimated_cost_usd", sa.Float(), nullable=True))
    op.add_column("replay_runs", sa.Column("actual_cost_usd", sa.Float(), nullable=True))
    op.add_column("replay_runs", sa.Column("error_message", sa.Text(), nullable=True))
    op.add_column("replay_runs", sa.Column("llm_spans_count", sa.Integer(), nullable=True, server_default="0"))
    op.add_column("replay_runs", sa.Column("project_id", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("replay_runs", "project_id")
    op.drop_column("replay_runs", "llm_spans_count")
    op.drop_column("replay_runs", "error_message")
    op.drop_column("replay_runs", "actual_cost_usd")
    op.drop_column("replay_runs", "estimated_cost_usd")

    op.drop_index("ix_notifications_read", table_name="notifications")
    op.drop_index("ix_notifications_project_id", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_project_settings_project_id", table_name="project_settings")
    op.drop_table("project_settings")
