"""Graph database client wrapper around the Neo4j driver.

Every query is wrapped so a missing/unreachable Neo4j instance logs a
warning and returns an empty result instead of crashing the caller - the
same graceful-degradation contract `backend/ingestion/base_collector.py`
uses for external data sources.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from neo4j import GraphDatabase

logger = logging.getLogger(__name__)


class KGClient:
    """Thin wrapper around a Neo4j driver and session."""

    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
        unavailable_retry_seconds: float = 30.0,
        connection_timeout_seconds: float = 3.0,
    ):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "")
        self.database = database or os.getenv("NEO4J_DATABASE", "neo4j")
        # The driver's own default connection timeout is tens of seconds
        # (meant for real network hiccups against a server that's actually
        # up); every API request that touches the graph would otherwise
        # block that long before falling back, whenever Neo4j simply isn't
        # running yet. A few seconds is enough to distinguish "unreachable"
        # from "slow" while keeping graceful degradation actually graceful.
        self._connection_timeout_seconds = connection_timeout_seconds
        self._driver = None
        # Once a connection attempt fails, every caller in the process
        # (dozens of run_query calls per event/risk-score pipeline run)
        # would otherwise retry the full TCP handshake and log its own
        # multi-line "connection refused" warning. Backing off for a
        # window after the first failure turns that wall of noise into one
        # clear warning, while still auto-recovering once Neo4j comes up
        # without requiring an app restart.
        self._unavailable_retry_seconds = unavailable_retry_seconds
        self._unavailable_since: float | None = None

    def _get_driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                connection_timeout=self._connection_timeout_seconds,
            )
        return self._driver

    def _in_backoff(self) -> bool:
        if self._unavailable_since is None:
            return False
        return (time.monotonic() - self._unavailable_since) < self._unavailable_retry_seconds

    def health(self) -> bool:
        """Returns True if Neo4j is reachable, without raising."""
        try:
            self._get_driver().verify_connectivity()
            self._unavailable_since = None
            return True
        except Exception as exc:  # noqa: BLE001 - external service, must not crash caller
            logger.warning("Neo4j health check failed: %s", exc)
            self._unavailable_since = time.monotonic()
            return False

    def run_query(self, cypher: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Runs a Cypher statement and returns each record as a plain dict.

        Used for both reads and writes (MERGE/SET); on any failure this
        logs and returns `[]` rather than propagating, per Planning
        Principle "every collector/query should degrade gracefully". Skips
        the network attempt entirely while a prior failure's backoff
        window is still active (see `__init__`).
        """
        if self._in_backoff():
            return []
        try:
            driver = self._get_driver()
            with driver.session(database=self.database) as session:
                result = session.run(cypher, parameters or {})
                records = [record.data() for record in result]
            self._unavailable_since = None
            return records
        except Exception as exc:  # noqa: BLE001 - external service, must not crash caller
            if self._unavailable_since is None:
                logger.warning(
                    "Neo4j unreachable at %s; graph queries will return [] for the next %.0fs: %s",
                    self.uri,
                    self._unavailable_retry_seconds,
                    exc,
                )
            self._unavailable_since = time.monotonic()
            return []

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None


_default_client: KGClient | None = None


def get_kg_client() -> KGClient:
    """Returns the process-wide KGClient singleton (lazy connect)."""
    global _default_client
    if _default_client is None:
        _default_client = KGClient()
    return _default_client
