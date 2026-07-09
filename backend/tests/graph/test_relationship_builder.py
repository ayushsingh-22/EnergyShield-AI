from datetime import datetime, timezone

from graph import relationship_builder
from models.core_schema import CommodityType, RiskEventType, SourceReliability
from models.event_schema import RiskEvent


class _FakeKGClient:
    def __init__(self, match_targets):
        """`match_targets` is the set of entity_ids the fake graph "knows
        about" - MATCH on any other id returns no rows, mirroring Neo4j."""
        self.match_targets = match_targets
        self.calls = []

    def run_query(self, cypher, parameters=None):
        parameters = parameters or {}
        self.calls.append((cypher, parameters))
        if "SET r.expired_at = datetime()" in cypher:
            return [{"target_id": t} for t in self.match_targets]
        if "MERGE (evt)-[r:AFFECTS]->(target)" in cypher:
            if parameters.get("target_id") in self.match_targets:
                return [{"target_id": parameters["target_id"]}]
            return []
        if "MERGE (evt:RiskEvent" in cypher:
            return [{"entity_id": parameters.get("entity_id")}]
        return []


def _make_event(affected_entities):
    return RiskEvent(
        event_id="EVT-2026-0001",
        event_type=RiskEventType.MARITIME_ATTACK,
        commodity_type=CommodityType.CRUDE_OIL,
        title="Tanker incident reported near Red Sea corridor",
        summary="Structured summary of the event",
        detected_at=datetime.now(timezone.utc),
        source_name="UKMTO",
        source_reliability=SourceReliability.HIGH,
        affected_entities=affected_entities,
        severity=4,
        confidence=0.82,
    )


def test_upsert_event_relationships_creates_edges_for_known_entities():
    fake = _FakeKGClient(match_targets={"CHK_BAB"})
    event = _make_event(["CHK_BAB"])

    edge_count = relationship_builder.upsert_event_relationships(event, client=fake)

    assert edge_count == 1


def test_upsert_event_relationships_skips_unknown_entities():
    fake = _FakeKGClient(match_targets={"CHK_BAB"})
    event = _make_event(["CHK_BAB", "UNKNOWN_ENTITY"])

    edge_count = relationship_builder.upsert_event_relationships(event, client=fake)

    assert edge_count == 1


def test_expire_event_relationships_returns_expired_count():
    fake = _FakeKGClient(match_targets={"CHK_BAB", "RT_RED_SEA"})

    expired = relationship_builder.expire_event_relationships("EVT-2026-0001", client=fake)

    assert expired == 2
