from datetime import datetime, timezone

from models.core_schema import CommodityType, EntityType, RiskLevel
from models.risk_schema import RiskScore
from models.scenario_schema import ScenarioType
from workers.scenario_worker import find_triggered_scenario_requests


def _score(entity_id, risk_score) -> RiskScore:
    return RiskScore(
        entity_id=entity_id,
        entity_type=EntityType.CHOKEPOINT,
        commodity_type=CommodityType.CRUDE_OIL,
        risk_score=risk_score,
        risk_level=RiskLevel.HIGH,
        confidence=0.8,
        updated_at=datetime.now(timezone.utc),
    )


def test_score_above_threshold_with_known_entity_triggers_request():
    requests = find_triggered_scenario_requests([_score("CHK_HORMUZ", 85.0)], threshold=70.0)
    assert len(requests) == 1
    assert requests[0].scenario_type == ScenarioType.HORMUZ_PARTIAL_CLOSURE
    assert requests[0].severity == RiskLevel.SEVERE


def test_score_above_threshold_but_unknown_entity_does_not_trigger():
    requests = find_triggered_scenario_requests([_score("REF_JAM", 95.0)], threshold=70.0)
    assert requests == []


def test_score_below_threshold_does_not_trigger():
    requests = find_triggered_scenario_requests([_score("CHK_HORMUZ", 50.0)], threshold=70.0)
    assert requests == []


def test_very_high_score_uses_critical_severity():
    requests = find_triggered_scenario_requests([_score("CHK_HORMUZ", 95.0)], threshold=70.0)
    assert requests[0].severity == RiskLevel.CRITICAL
