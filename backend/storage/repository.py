"""Persistence abstraction for relational DB (Phase 8, section 8.1).

Tables are intentionally generic (id, an entity/scenario/etc. key, a JSON
payload, timestamps) rather than one column per Pydantic field: the
Pydantic schemas in `backend/models/` are the actual frozen contract
(Planning Principle #10), so the relational layer's job is durable storage
and lookup-by-key, not re-modelling fields SQLAlchemy would only have to
stay in sync with by hand.

Every write/read goes through `db.session.session_scope()` and is
best-effort: if Postgres is unreachable, the call is a no-op (write) or
returns `[]` (read) rather than raising, so every service keeps working
from its own in-memory state with no database running - the same
graceful-degradation contract already used for Neo4j (`graph/kg_client.py`)
and external data sources (`ingestion/base_collector.py`).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, MetaData, String, Table, Text, select

from db.session import session_scope

logger = logging.getLogger(__name__)

metadata = MetaData()


class _JsonTable:
    """A `Table` plus the name of its lookup-key column, so callers never
    have to guess which column to filter/insert by."""

    def __init__(self, name: str, key_column: str):
        self.key_column = key_column
        self.table = Table(
            name,
            metadata,
            Column("id", String, primary_key=True),
            Column(key_column, String, index=True, nullable=False),
            Column("payload", Text, nullable=False),
            Column("created_at", DateTime(timezone=True), nullable=False),
        )

    def save(self, row_id: str, key_value: str, payload_json: str) -> None:
        with session_scope() as session:
            if session is None:
                return
            session.execute(self.table.delete().where(self.table.c.id == row_id))
            session.execute(
                self.table.insert().values(
                    id=row_id,
                    **{self.key_column: key_value},
                    payload=payload_json,
                    created_at=datetime.now(timezone.utc),
                )
            )

    def query(self, key_value: str) -> list[dict[str, Any]]:
        with session_scope() as session:
            if session is None:
                return []
            try:
                rows = session.execute(
                    select(self.table)
                    .where(getattr(self.table.c, self.key_column) == key_value)
                    .order_by(self.table.c.created_at)
                ).fetchall()
                return [dict(row._mapping) for row in rows]
            except Exception:  # noqa: BLE001 - table may not exist yet if init_db() hasn't run
                logger.info("Query against '%s' skipped (table missing or DB unavailable); returning no rows.", self.table.name)
                return []


data_sources = _JsonTable("data_sources", "source_name")
raw_records = _JsonTable("raw_records", "source_name")
normalized_signals = _JsonTable("normalized_signals", "source_name")
risk_events = _JsonTable("risk_events", "event_id")
risk_scores = _JsonTable("risk_scores", "entity_id")
scenario_runs = _JsonTable("scenario_runs", "scenario_id")
recommendations = _JsonTable("recommendations", "scenario_id")
audit_events = _JsonTable("audit_events", "entity_id")
generated_reports = _JsonTable("generated_reports", "scenario_id")


def save_data_source(source_name: str, payload_json: str) -> None:
    data_sources.save(source_name, source_name, payload_json)


def save_raw_record(record_id: str, source_name: str, payload_json: str) -> None:
    raw_records.save(record_id, source_name, payload_json)


def save_normalized_signal(signal_id: str, source_name: str, payload_json: str) -> None:
    normalized_signals.save(signal_id, source_name, payload_json)


def save_risk_event(event_id: str, payload_json: str) -> None:
    risk_events.save(event_id, event_id, payload_json)


def save_risk_score(entity_id: str, payload_json: str) -> None:
    risk_scores.save(f"{entity_id}:{datetime.now(timezone.utc).isoformat()}", entity_id, payload_json)


def save_scenario_run(scenario_id: str, payload_json: str) -> None:
    scenario_runs.save(scenario_id, scenario_id, payload_json)


def save_recommendation(recommendation_id: str, scenario_id: str, payload_json: str) -> None:
    recommendations.save(recommendation_id, scenario_id, payload_json)


def save_audit_event(audit_id: str, entity_id: str, payload_json: str) -> None:
    audit_events.save(audit_id, entity_id, payload_json)


def save_generated_report(report_id: str, scenario_id: str, payload_json: str) -> None:
    generated_reports.save(report_id, scenario_id, payload_json)


def get_audit_events_for_entity(entity_id: str) -> list[dict[str, Any]]:
    return audit_events.query(entity_id)


def get_scenario_run(scenario_id: str) -> list[dict[str, Any]]:
    return scenario_runs.query(scenario_id)


def get_recommendation_for_scenario(scenario_id: str) -> list[dict[str, Any]]:
    return recommendations.query(scenario_id)
