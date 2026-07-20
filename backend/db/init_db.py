"""Creates and initializes tables: data_sources, raw_records, normalized_signals, risk_events,
risk_scores, scenario_runs, recommendations, audit_events, generated_reports."""

from __future__ import annotations

import logging

from db.session import get_engine
from storage.repository import metadata

logger = logging.getLogger(__name__)


def _short_reason(exc: Exception) -> str:
    """Innermost concise reason (e.g. 'connection timeout expired') without
    the full SQLAlchemy exception chain / traceback."""
    reason = str(exc.__cause__ or exc).strip().splitlines()
    return reason[0] if reason else exc.__class__.__name__


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
        logger.info("Postgres reachable; persistence tables ready.")
        return True
    except Exception as exc:  # noqa: BLE001 - external service, must not crash app startup
        # A missing Postgres is an expected, first-class no-database mode -
        # not an error worth a multi-line traceback on every startup. Log
        # one concise line (without the SQLAlchemy stack) and carry on with
        # in-memory service state; `docker-compose up postgres` +
        # `alembic upgrade head` turns real persistence on when wanted.
        logger.info(
            "Postgres not reachable; running with in-memory state only (persistence disabled). Reason: %s",
            _short_reason(exc),
        )
        return False
