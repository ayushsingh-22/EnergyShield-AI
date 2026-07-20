from datetime import datetime, timezone

from graph import risk_graph_updater
from models.core_schema import CommodityType, EntityType, RiskLevel
from models.risk_schema import RiskScore


class _FakeKGClient:
    def __init__(self, match_targets, available=True):
        self.match_targets = match_targets
        self._available = available
        self.calls = []

    def is_available(self) -> bool:
        return self._available

    def run_query(self, cypher, parameters=None):
        parameters = parameters or {}
        self.calls.append((cypher, parameters))
        if "RETURN n.entity_id AS entity_id" in cypher:
            if parameters.get("entity_id") in self.match_targets:
                return [{"entity_id": parameters["entity_id"]}]
            return []
        return [{"ok": True}]


def _score(entity_id, evidence_event_ids=None):
    return RiskScore(
        entity_id=entity_id,
        entity_type=EntityType.CHOKEPOINT,
        commodity_type=CommodityType.CRUDE_OIL,
        risk_score=75.0,
        risk_level=RiskLevel.SEVERE,
        evidence_event_ids=evidence_event_ids or [],
        confidence=0.8,
        updated_at=datetime.now(timezone.utc),
    )


def test_update_risk_score_writes_node_properties_for_known_entity():
    fake = _FakeKGClient(match_targets={"CHK_HORMUZ"})

    updated = risk_graph_updater.update_risk_score(_score("CHK_HORMUZ"), client=fake)

    assert updated is True
    node_update_calls = [call for call in fake.calls if "SET n.risk_score" in call[0]]
    assert node_update_calls
    assert node_update_calls[0][1]["risk_score"] == 75.0


def test_update_risk_score_skips_unknown_entity():
    fake = _FakeKGClient(match_targets=set())

    updated = risk_graph_updater.update_risk_score(_score("CHK_UNKNOWN"), client=fake)

    assert updated is False


def test_update_risk_score_links_evidence_events():
    fake = _FakeKGClient(match_targets={"CHK_HORMUZ"})

    risk_graph_updater.update_risk_score(_score("CHK_HORMUZ", evidence_event_ids=["EVT-1", "EVT-2"]), client=fake)

    evidence_calls = [call for call in fake.calls if "EVIDENCED_BY" in call[0]]
    assert len(evidence_calls) == 2


def test_update_risk_scores_counts_only_successful_updates():
    fake = _FakeKGClient(match_targets={"CHK_HORMUZ"})
    scores = [_score("CHK_HORMUZ"), _score("CHK_UNKNOWN")]

    updated_count = risk_graph_updater.update_risk_scores(scores, client=fake)

    assert updated_count == 1


def test_update_risk_scores_skips_quietly_when_graph_unavailable():
    """With no Neo4j running, the whole batch is skipped without a
    per-entity 'unknown graph entity' warning (returns 0, no queries)."""
    fake = _FakeKGClient(match_targets={"CHK_HORMUZ"}, available=False)
    scores = [_score("CHK_HORMUZ"), _score("CHK_UNKNOWN")]

    updated_count = risk_graph_updater.update_risk_scores(scores, client=fake)

    assert updated_count == 0
    assert fake.calls == []
