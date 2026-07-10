"""Pushes latest corridor, supplier, and refinery risk scores back into
graph node properties (Phase 5, section 5.4).

Mirrors the graceful-degradation contract every other graph write already
follows (`graph/relationship_builder.py`, `graph/kg_client.py`): an
unreachable Neo4j instance must not break the risk API, and a score for an
entity_id the graph doesn't know about is logged and skipped rather than
creating a dangling node.
"""

from __future__ import annotations

import logging

from graph.kg_client import KGClient, get_kg_client
from models.risk_schema import RiskScore

logger = logging.getLogger(__name__)


def update_risk_score(score: RiskScore, client: KGClient | None = None) -> bool:
    """Writes `risk_score` / `risk_level` / `last_risk_update` onto the
    graph node for `score.entity_id` (step 1: "update node properties"),
    records a `RiskScoreSnapshot` history node linked to it via
    `HAS_RISK_SCORE` (step 2: "create score history entries"), and links
    that snapshot to every evidence event via `EVIDENCED_BY` (step 3:
    "link scores to evidence events"). Returns True if the target entity
    exists and was updated.
    """
    client = client or get_kg_client()

    matched = client.run_query(
        """
        MATCH (n {entity_id: $entity_id})
        SET n.risk_score = $risk_score,
            n.risk_level = $risk_level,
            n.last_risk_update = $updated_at
        RETURN n.entity_id AS entity_id
        """,
        {
            "entity_id": score.entity_id,
            "risk_score": score.risk_score,
            "risk_level": score.risk_level,
            "updated_at": score.updated_at.isoformat(),
        },
    )
    if not matched:
        logger.warning("Risk score computed for unknown graph entity '%s'; node update skipped", score.entity_id)
        return False

    snapshot_id = f"RISKSNAP-{score.entity_id}-{score.updated_at.isoformat()}"
    client.run_query(
        """
        MATCH (n {entity_id: $entity_id})
        MERGE (snap:RiskScoreSnapshot {entity_id: $snapshot_id})
        SET snap.risk_score = $risk_score, snap.risk_level = $risk_level,
            snap.recorded_at = $updated_at
        MERGE (n)-[:HAS_RISK_SCORE]->(snap)
        """,
        {
            "entity_id": score.entity_id,
            "snapshot_id": snapshot_id,
            "risk_score": score.risk_score,
            "risk_level": score.risk_level,
            "updated_at": score.updated_at.isoformat(),
        },
    )

    for event_id in score.evidence_event_ids:
        client.run_query(
            """
            MATCH (snap:RiskScoreSnapshot {entity_id: $snapshot_id})
            MATCH (evt:RiskEvent {entity_id: $event_id})
            MERGE (snap)-[:EVIDENCED_BY]->(evt)
            """,
            {"snapshot_id": snapshot_id, "event_id": event_id},
        )

    return True


def update_risk_scores(scores: list[RiskScore], client: KGClient | None = None) -> int:
    """Updates every score in `scores`. Never raises - one bad write (or an
    unreachable graph entirely) must not break the risk API. Returns the
    number of scores successfully written."""
    client = client or get_kg_client()
    updated = 0
    for score in scores:
        try:
            if update_risk_score(score, client=client):
                updated += 1
        except Exception:  # noqa: BLE001 - one bad write must not break the batch
            logger.exception("Failed to push risk score for entity '%s' into graph", score.entity_id)
    return updated
