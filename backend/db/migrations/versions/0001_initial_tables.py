"""Initial persistence tables (Phase 8, section 8.1)

Revision ID: 0001
Revises:
Create Date: 2026-07-20

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = {
    "data_sources": "source_name",
    "raw_records": "source_name",
    "normalized_signals": "source_name",
    "risk_events": "event_id",
    "risk_scores": "entity_id",
    "scenario_runs": "scenario_id",
    "recommendations": "scenario_id",
    "audit_events": "entity_id",
    "generated_reports": "scenario_id",
}


def upgrade() -> None:
    for table_name, key_column in _TABLES.items():
        op.create_table(
            table_name,
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column(key_column, sa.String(), nullable=False),
            sa.Column("payload", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index(f"ix_{table_name}_{key_column}", table_name, [key_column])


def downgrade() -> None:
    for table_name in _TABLES:
        op.drop_table(table_name)
