"""Graph database client wrapper around the Neo4j driver.

Every query is wrapped so a missing/unreachable Neo4j instance logs a
warning and returns an empty result instead of crashing the caller - the
same graceful-degradation contract `backend/ingestion/base_collector.py`
uses for external data sources.
"""

from __future__ import annotations

import logging
import os
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
    ):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "")
        self.database = database or os.getenv("NEO4J_DATABASE", "neo4j")
        self._driver = None

    def _get_driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self._driver

    def health(self) -> bool:
        """Returns True if Neo4j is reachable, without raising."""
        try:
            self._get_driver().verify_connectivity()
            return True
        except Exception as exc:  # noqa: BLE001 - external service, must not crash caller
            logger.warning("Neo4j health check failed: %s", exc)
            return False

    def run_query(self, cypher: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Runs a Cypher statement and returns each record as a plain dict.

        Used for both reads and writes (MERGE/SET); on any failure this
        logs and returns `[]` rather than propagating, per Planning
        Principle "every collector/query should degrade gracefully".
        """
        try:
            driver = self._get_driver()
            with driver.session(database=self.database) as session:
                result = session.run(cypher, parameters or {})
                return [record.data() for record in result]
        except Exception as exc:  # noqa: BLE001 - external service, must not crash caller
            logger.warning("Graph query failed, returning empty result: %s", exc)
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
