"""Creates and initializes tables: data_sources, raw_records, normalized_signals, risk_events,
risk_scores, scenario_runs, recommendations, audit_events, generated_reports."""

from __future__ import annotations

import logging

from db.session import get_engine
from storage.repository import metadata

logger = logging.getLogger(__name__)


def init_db() -> bool:
    """Creates every table in `storage.repository.metadata` if it doesn't
    already exist. Called once at app startup (`main.py`); returns `False`
    instead of raising when Postgres is unreachable, so a missing database
    never prevents the API from serving requests from in-memory state -
    real persistence and the Alembic migrations in `db/migrations/` take
    over once Postgres is actually running (`docker-compose up postgres`).
    """
    try:
        metadata.create_all(get_engine())
        return True
    except Exception:  # noqa: BLE001 - external service, must not crash app startup
        logger.warning("Database unreachable; continuing with in-memory service state only.", exc_info=True)
        return False
