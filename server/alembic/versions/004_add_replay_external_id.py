"""Add replay_runs table and external_id column on traces.

Revision ID: 004
Revises: 003
Create Date: 2024-06-20 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add external_id to traces
    op.add_column("traces", sa.Column("external_id", sa.String(256), nullable=True))
    op.create_index("ix_traces_external_id", "traces", ["external_id"], unique=True)

    # Create replay_runs table
    op.create_table(
        "replay_runs",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("original_trace_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("created_by", sa.String(length=320), nullable=True),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("result_trace_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["original_trace_id"], ["traces.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_replay_runs_original_trace_id", "replay_runs", ["original_trace_id"])


def downgrade() -> None:
    op.drop_index("ix_replay_runs_original_trace_id", table_name="replay_runs")
    op.drop_table("replay_runs")
    op.drop_index("ix_traces_external_id", table_name="traces")
    op.drop_column("traces", "external_id")
