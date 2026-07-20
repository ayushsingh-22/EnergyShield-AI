from datetime import datetime, timezone

import pytest

from agents.geopolitical_risk_agent import GeopoliticalRiskAgent
from models.core_schema import CommodityType, RiskEventType, SourceReliability
from models.event_schema import RiskEvent
from services.digital_twin_service import DigitalTwinService
from services.event_service import EventService
from services.risk_service import RiskService


@pytest.fixture(autouse=True)
def _skip_graph_push(monkeypatch):
    monkeypatch.setattr("services.risk_service.update_risk_scores", lambda scores: 0)


def _digital_twin() -> DigitalTwinService:
    service = DigitalTwinService()
    service.load_seed_data()
    return service


def _event(event_id, affected_entities, severity=5) -> RiskEvent:
    return RiskEvent(
        event_id=event_id,
        event_type=RiskEventType.MARITIME_ATTACK,
        commodity_type=CommodityType.CRUDE_OIL,
        title="t",
        summary="s",
        detected_at=datetime.now(timezone.utc),
        source_name="test",
        source_reliability=SourceReliability.OFFICIAL,
        affected_entities=affected_entities,
        severity=severity,
        confidence=0.9,
    )


def test_get_risk_briefing_returns_all_three_entity_groups():
    risk_service = RiskService(digital_twin=_digital_twin(), event_service=EventService())
    agent = GeopoliticalRiskAgent(risk_service=risk_service)

    briefing = agent.get_risk_briefing()

    assert set(briefing.keys()) == {"corridors", "suppliers", "refineries"}
    assert briefing["corridors"]
    assert briefing["suppliers"]


def test_get_top_concerns_ranks_by_score_descending_across_entity_types():
    events = EventService()
    events.add_event(_event("EVT-1", ["CHK_HORMUZ"], severity=5))
    risk_service = RiskService(digital_twin=_digital_twin(), event_service=events)
    agent = GeopoliticalRiskAgent(risk_service=risk_service)

    top = agent.get_top_concerns(limit=3)

    assert len(top) <= 3
    scores = [entry.risk_score for entry in top]
    assert scores == sorted(scores, reverse=True)
    # The severity-5 event on CHK_HORMUZ should push either the chokepoint
    # itself or a refinery exposed through it to the top of the ranking -
    # exactly which one depends on risk_scoring_engine's exposure/reliability
    # weighting, not on GeopoliticalRiskAgent's own (thin) ranking logic.
    assert top[0].risk_score > 0
    assert top[0].evidence_event_ids


def test_get_top_concerns_respects_limit():
    risk_service = RiskService(digital_twin=_digital_twin(), event_service=EventService())
    agent = GeopoliticalRiskAgent(risk_service=risk_service)

    assert len(agent.get_top_concerns(limit=2)) == 2
