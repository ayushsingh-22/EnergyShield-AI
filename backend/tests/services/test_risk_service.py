from datetime import datetime, timezone

import pytest

from models.core_schema import CommodityType, RiskEventType, SourceReliability
from models.event_schema import RiskEvent
from services.digital_twin_service import DigitalTwinService
from services.event_service import EventService
from services.risk_service import RiskService


@pytest.fixture(autouse=True)
def _skip_graph_push(monkeypatch):
    # These are RiskService unit tests - the graph-write behavior itself is
    # covered by tests/graph/test_risk_graph_updater.py with a fake KGClient.
    monkeypatch.setattr("services.risk_service.update_risk_scores", lambda scores: 0)


def _digital_twin() -> DigitalTwinService:
    service = DigitalTwinService()
    service.load_seed_data()
    return service


def _event(event_id, affected_entities, severity=5, reliability=SourceReliability.OFFICIAL):
    return RiskEvent(
        event_id=event_id,
        event_type=RiskEventType.MARITIME_ATTACK,
        commodity_type=CommodityType.CRUDE_OIL,
        title="t",
        summary="s",
        detected_at=datetime.now(timezone.utc),
        source_name="test",
        source_reliability=reliability,
        affected_entities=affected_entities,
        severity=severity,
        confidence=0.8,
    )


def test_get_corridors_returns_only_corridor_entities():
    service = RiskService(digital_twin=_digital_twin(), event_service=EventService())

    corridors = service.get_corridors()

    assert corridors
    assert all(score.entity_type in ("CHOKEPOINT", "SHIPPING_ROUTE") for score in corridors)


def test_get_suppliers_returns_only_supplier_entities():
    service = RiskService(digital_twin=_digital_twin(), event_service=EventService())

    suppliers = service.get_suppliers()

    assert suppliers
    assert all(score.entity_type == "SUPPLIER_COUNTRY" for score in suppliers)


def test_score_changes_when_high_severity_event_added():
    """Phase 5 validation: 'risk score changes when a high-severity event is added.'"""
    event_service = EventService()
    service = RiskService(digital_twin=_digital_twin(), event_service=event_service)

    baseline = next(s for s in service.get_corridors() if s.entity_id == "CHK_HORMUZ")

    event_service.add_event(_event("EVT-1", ["CHK_HORMUZ"]))
    stressed = next(s for s in service.get_corridors() if s.entity_id == "CHK_HORMUZ")

    assert stressed.risk_score > baseline.risk_score
    assert stressed.previous_score == baseline.risk_score
    assert stressed.delta == round(stressed.risk_score - baseline.risk_score, 1)


def test_score_decreases_when_event_resolved():
    """Phase 5 validation: 'risk score decreases when event is resolved or expires.'"""
    event_service = EventService()
    service = RiskService(digital_twin=_digital_twin(), event_service=event_service)

    event_service.add_event(_event("EVT-1", ["CHK_HORMUZ"]))
    stressed = next(s for s in service.get_corridors() if s.entity_id == "CHK_HORMUZ")

    event_service.replace_all([])  # event resolved / expired
    resolved = next(s for s in service.get_corridors() if s.entity_id == "CHK_HORMUZ")

    assert resolved.risk_score < stressed.risk_score


def test_history_grows_only_on_actual_change():
    """Phase 5 validation: 'risk history is stored for trend charts.'"""
    event_service = EventService()
    service = RiskService(digital_twin=_digital_twin(), event_service=event_service)

    service.get_corridors()  # baseline
    service.get_corridors()  # no change - must not duplicate
    assert len(service.get_history("CHK_HORMUZ")) == 1

    event_service.add_event(_event("EVT-1", ["CHK_HORMUZ"]))
    service.get_corridors()
    assert len(service.get_history("CHK_HORMUZ")) == 2


def test_get_history_unknown_entity_is_empty():
    service = RiskService(digital_twin=_digital_twin(), event_service=EventService())
    assert service.get_history("UNKNOWN") == []


def test_refresh_without_event_service_scores_from_baseline_exposure_only():
    service = RiskService(digital_twin=_digital_twin(), event_service=None)

    corridors = service.get_corridors()

    assert corridors
    assert all(score.evidence_event_ids == [] for score in corridors)


def test_history_is_capped_for_long_running_processes():
    """A long-running process that keeps seeing genuine score changes must
    not accumulate an unbounded per-entity history list."""
    import services.risk_service as risk_service_module

    event_service = EventService()
    service = RiskService(digital_twin=_digital_twin(), event_service=event_service)
    cap = risk_service_module._MAX_HISTORY_ENTRIES_PER_ENTITY

    for i in range(cap + 20):
        event_service.replace_all([_event(f"EVT-{i}", ["CHK_HORMUZ"], severity=((i % 4) + 1))])
        service.get_corridors()

    history = service.get_history("CHK_HORMUZ")
    assert len(history) <= cap
