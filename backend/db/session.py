"""Database session and connection handling for PostgreSQL persistence."""

from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

_engine: Engine | None = None
_SessionFactory: sessionmaker | None = None
_unavailable_warned = False

# Once a connection fails, every subsequent write/read would otherwise pay
# the full `connect_timeout` again (3s each) and re-log - turning a
# no-database run into a slow, noisy one. Back off for a window after the
# first failure (same pattern as `graph/kg_client.py`): skip the network
# attempt entirely and yield None immediately, while still auto-recovering
# once Postgres comes up without an app restart.
_UNAVAILABLE_RETRY_SECONDS = float(os.getenv("DB_UNAVAILABLE_RETRY_SECONDS", "30"))
_unavailable_since: float | None = None


def _in_backoff() -> bool:
    if _unavailable_since is None:
        return False
    return (time.monotonic() - _unavailable_since) < _UNAVAILABLE_RETRY_SECONDS


def get_engine() -> Engine:
    """Lazily creates the process-wide SQLAlchemy engine. Creating an
    `Engine` does not open a connection - the same lazy-connect contract
    `graph/kg_client.py` uses for Neo4j - so importing this module never
    requires a reachable Postgres."""
    global _engine, _SessionFactory
    if _engine is None:
        database_url = os.getenv(
            "DATABASE_URL", "postgresql+psycopg://energyshield:change-me@localhost:5432/energyshield"
        )
        # Without an explicit timeout, a first connection attempt against
        # an unreachable/not-yet-started Postgres can block for a long
        # time (OS-level TCP timeout) before every write in
        # `storage/repository.py` falls back to "skip persistence" - the
        # same reasoning behind `graph/kg_client.py`'s short Neo4j
        # connection timeout.
        _engine = create_engine(database_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        _SessionFactory = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


@contextmanager
def session_scope() -> Iterator[Session | None]:
    """Yields a `Session`, or `None` if Postgres is unreachable.

    Every table write in `backend/storage/repository.py` goes through this
    and treats a `None` session as "skip persistence for this call" rather
    than crashing - the same graceful-degradation contract
    `graph/kg_client.KGClient.run_query` uses for Neo4j, so services stay
    fully functional (reading/writing their own in-memory state) with no
    database running.
    """
    global _unavailable_warned, _unavailable_since
    # Skip the network round-trip entirely while a prior failure's backoff
    # window is still active - keeps the live API fast in a no-database run.
    if _in_backoff():
        yield None
        return

    get_engine()
    assert _SessionFactory is not None
    try:
        session = _SessionFactory()
    except Exception:  # noqa: BLE001 - external service, must not crash caller
        if not _unavailable_warned:
            logger.info("Postgres unavailable; persistence calls will be skipped for the next %.0fs.", _UNAVAILABLE_RETRY_SECONDS)
            _unavailable_warned = True
        _unavailable_since = time.monotonic()
        yield None
        return

    try:
        yield session
        session.commit()
        _unavailable_warned = False
        _unavailable_since = None
    except Exception:  # noqa: BLE001 - external service, must not crash caller
        session.rollback()
        if not _unavailable_warned:
            logger.info("Postgres write failed; persistence calls will be skipped for the next %.0fs.", _UNAVAILABLE_RETRY_SECONDS)
            _unavailable_warned = True
        _unavailable_since = time.monotonic()
    finally:
        session.close()
