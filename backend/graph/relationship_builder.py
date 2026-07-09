"""Converts new risk events into graph AFFECTS edges and expires resolved event edges.

Phase 4's event extraction agent will call `upsert_event_relationships` for
every extracted `RiskEvent`; risk scoring and scenario modelling then read
active AFFECTS edges instead of hardcoding which entities an event touches.
"""

from __future__ import annotations

import logging
from typing import Any

from graph.kg_client import KGClient, get_kg_client
from models.event_schema import RiskEvent

logger = logging.getLogger(__name__)


def _event_properties(event: RiskEvent) -> dict[str, Any]:
    props = {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "commodity_type": event.commodity_type,
        "title": event.title,
        "summary": event.summary,
        "severity": event.severity,
        "confidence": event.confidence,
        "source_name": event.source_name,
        "source_reliability": event.source_reliability,
        "detected_at": event.detected_at.isoformat() if event.detected_at else None,
        "is_simulated": event.is_simulated,
    }
    return {key: value for key, value in props.items() if value is not None}


def upsert_event_relationships(event: RiskEvent, client: KGClient | None = None) -> int:
    """Creates/updates the RiskEvent node and an AFFECTS edge to every
    entity in `event.affected_entities` (Phase 3, section 3.3).

    Returns the number of AFFECTS edges created or refreshed. An
    `affected_entities` id that doesn't match any existing graph node is
    logged and skipped rather than raising, since event extraction may
    resolve entities the graph hasn't been seeded with yet.
    """
    client = client or get_kg_client()

    client.run_query(
        "MERGE (evt:RiskEvent {entity_id: $entity_id}) SET evt += $properties",
        {"entity_id": event.event_id, "properties": _event_properties(event)},
    )

    edge_count = 0
    for target_id in event.affected_entities:
        result = client.run_query(
            """
            MATCH (evt:RiskEvent {entity_id: $event_id})
            MATCH (target {entity_id: $target_id})
            MERGE (evt)-[r:AFFECTS]->(target)
            SET r.confidence = $confidence,
                r.severity = $severity,
                r.detected_at = $detected_at,
                r.expired_at = NULL
            RETURN target.entity_id AS target_id
            """,
            {
                "event_id": event.event_id,
                "target_id": target_id,
                "confidence": event.confidence,
                "severity": event.severity,
                "detected_at": event.detected_at.isoformat() if event.detected_at else None,
            },
        )
        if result:
            edge_count += 1
        else:
            logger.warning(
                "RiskEvent %s references unknown affected entity '%s'; AFFECTS edge skipped",
                event.event_id,
                target_id,
            )
    return edge_count


def expire_event_relationships(event_id: str, client: KGClient | None = None) -> int:
    """Marks all active AFFECTS edges from a resolved/expired event.

    Edges are marked with `expired_at` rather than deleted so historical
    risk context survives for the continuous-learning track (Phase 13).
    Returns the number of edges expired.
    """
    client = client or get_kg_client()
    rows = client.run_query(
        """
        MATCH (evt:RiskEvent {entity_id: $event_id})-[r:AFFECTS]->(target)
        WHERE r.expired_at IS NULL
        SET r.expired_at = datetime()
        RETURN target.entity_id AS target_id
        """,
        {"event_id": event_id},
    )
    return len(rows)
