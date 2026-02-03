"""Add performance indexes for common query patterns.

Revision ID: 002
Revises: 001
Create Date: 2024-06-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Span indexes for filtering and sorting
    op.create_index("ix_spans_kind", "spans", ["kind"])
    op.create_index("ix_spans_status", "spans", ["status"])
    op.create_index("ix_spans_start_time", "spans", ["start_time"])
    op.create_index("ix_spans_created_at", "spans", ["created_at"])

    # Drift alert indexes
    op.create_index("ix_drift_alerts_resolved", "drift_alerts", ["resolved"])
    op.create_index("ix_drift_alerts_severity", "drift_alerts", ["severity"])

    # Trace indexes
    op.create_index("ix_traces_created_at", "traces", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_traces_created_at", table_name="traces")
    op.drop_index("ix_drift_alerts_severity", table_name="drift_alerts")
    op.drop_index("ix_drift_alerts_resolved", table_name="drift_alerts")
    op.drop_index("ix_spans_created_at", table_name="spans")
    op.drop_index("ix_spans_start_time", table_name="spans")
    op.drop_index("ix_spans_status", table_name="spans")
    op.drop_index("ix_spans_kind", table_name="spans")
