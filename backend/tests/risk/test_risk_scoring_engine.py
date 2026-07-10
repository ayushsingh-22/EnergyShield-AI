from datetime import datetime, timezone

from models.core_schema import CommodityType, RiskEventType, SourceReliability
from models.event_schema import RiskEvent
from risk.risk_scoring_engine import RiskScoringEngine
from services.digital_twin_service import DigitalTwinService


def _digital_twin() -> DigitalTwinService:
    service = DigitalTwinService()
    service.load_seed_data()
    return service


def _event(event_id, event_type, severity, affected_entities, source_name="gdelt", reliability=SourceReliability.MEDIUM):
    return RiskEvent(
        event_id=event_id,
        event_type=event_type,
        commodity_type=CommodityType.CRUDE_OIL,
        title="t",
        summary="s",
        detected_at=datetime.now(timezone.utc),
        source_name=source_name,
        source_reliability=reliability,
        affected_entities=affected_entities,
        severity=severity,
        confidence=0.7,
    )


def test_score_corridors_covers_every_chokepoint_and_route():
    twin = _digital_twin()
    engine = RiskScoringEngine(twin)

    scores = engine.score_corridors([])

    entity_ids = {score.entity_id for score in scores}
    expected = {chokepoint.id for chokepoint in twin.get_chokepoints()} | {route.id for route in twin.get_routes()}
    assert entity_ids == expected


def test_score_corridor_risk_increases_with_high_severity_event():
    """Phase 5 validation: 'risk score changes when a high-severity event is added.'"""
    twin = _digital_twin()
    engine = RiskScoringEngine(twin)

    baseline = next(s for s in engine.score_corridors([]) if s.entity_id == "CHK_HORMUZ")
    event = _event("EVT-1", RiskEventType.MARITIME_ATTACK, 5, ["CHK_HORMUZ"], reliability=SourceReliability.OFFICIAL)
    stressed = next(s for s in engine.score_corridors([event]) if s.entity_id == "CHK_HORMUZ")

    assert stressed.risk_score > baseline.risk_score
    assert stressed.evidence_event_ids == ["EVT-1"]
    assert any("High-severity" in driver for driver in stressed.top_drivers)


def test_score_corridor_risk_score_bounded_zero_to_hundred():
    twin = _digital_twin()
    engine = RiskScoringEngine(twin)
    events = [
        _event(
            f"EVT-{i}",
            RiskEventType.MARITIME_ATTACK,
            5,
            ["CHK_HORMUZ"],
            source_name=f"source-{i}",
            reliability=SourceReliability.OFFICIAL,
        )
        for i in range(10)
    ]

    hormuz = next(s for s in engine.score_corridors(events) if s.entity_id == "CHK_HORMUZ")

    assert 0.0 <= hormuz.risk_score <= 100.0


def test_score_suppliers_uses_sanctions_score_not_ais_anomaly():
    """Plan section 5.2, step 2: 'add sanctions score' - suppliers use a
    distinct sanctions-driven term instead of the AIS/route anomaly term
    corridors use, since a supplier country has no vessel movements of its
    own for an AIS anomaly to apply to."""
    twin = _digital_twin()
    engine = RiskScoringEngine(twin)

    baseline = next(s for s in engine.score_suppliers([]) if s.entity_id == "SUP_IRQ")
    sanction_event = _event(
        "EVT-1", RiskEventType.SANCTION_UPDATE, 5, ["SUP_IRQ"], reliability=SourceReliability.OFFICIAL
    )
    sanctioned = next(s for s in engine.score_suppliers([sanction_event]) if s.entity_id == "SUP_IRQ")

    assert sanctioned.risk_score > baseline.risk_score
    assert any("sanctions" in driver.lower() for driver in sanctioned.top_drivers)
    assert not any("ais" in driver.lower() for driver in sanctioned.top_drivers)


def test_score_corridors_uses_ais_anomaly_not_sanctions_score():
    """The inverse of the supplier case: an AIS/congestion event should
    still drive the corridor anomaly term and its driver text, not a
    sanctions-labelled one."""
    twin = _digital_twin()
    engine = RiskScoringEngine(twin)

    ais_event = _event(
        "EVT-1", RiskEventType.AIS_REROUTING, 4, ["CHK_HORMUZ"], reliability=SourceReliability.OFFICIAL
    )
    stressed = next(s for s in engine.score_corridors([ais_event]) if s.entity_id == "CHK_HORMUZ")

    assert any("ais" in driver.lower() for driver in stressed.top_drivers)


def test_score_suppliers_inherits_route_risk():
    """Plan section 5.2, step 3: 'add route risk for supplier's routes.'"""
    twin = _digital_twin()
    engine = RiskScoringEngine(twin)
    supplier = twin.find_supplier("SUP_IRQ")
    assert supplier.default_shipping_route_id == "RT_BAS_JAM"

    event = _event("EVT-1", RiskEventType.SANCTION_UPDATE, 5, ["RT_BAS_JAM"], reliability=SourceReliability.OFFICIAL)
    iraq_score = next(s for s in engine.score_suppliers([event]) if s.entity_id == "SUP_IRQ")

    assert "EVT-1" in iraq_score.evidence_event_ids


def test_score_refineries_exposed_via_stressed_chokepoint():
    """Plan section 5.3: refinery exposure score."""
    twin = _digital_twin()
    engine = RiskScoringEngine(twin)
    event = _event("EVT-1", RiskEventType.MARITIME_ATTACK, 5, ["CHK_HORMUZ"], reliability=SourceReliability.OFFICIAL)

    jamnagar_score = next(s for s in engine.score_refineries([event]) if s.entity_id == "REF_JAM")

    assert jamnagar_score.risk_score > 0
    assert "EVT-1" in jamnagar_score.evidence_event_ids


def test_score_refineries_zero_without_active_events():
    twin = _digital_twin()
    engine = RiskScoringEngine(twin)

    scores = engine.score_refineries([])

    assert all(score.evidence_event_ids == [] for score in scores)


def test_price_spike_uniformly_lifts_all_corridor_scores():
    twin = _digital_twin()
    engine = RiskScoringEngine(twin)
    price_event = _event("EVT-PRICE", RiskEventType.PRICE_SPIKE, 5, [], reliability=SourceReliability.HIGH)

    baseline = {s.entity_id: s.risk_score for s in engine.score_corridors([])}
    with_price_spike = {s.entity_id: s.risk_score for s in engine.score_corridors([price_event])}

    for entity_id, base_score in baseline.items():
        assert with_price_spike[entity_id] >= base_score


def test_score_all_combines_corridors_suppliers_and_refineries():
    twin = _digital_twin()
    engine = RiskScoringEngine(twin)

    scores = engine.score_all([])

    entity_types = {score.entity_type for score in scores}
    assert {"CHOKEPOINT", "SHIPPING_ROUTE", "SUPPLIER_COUNTRY", "REFINERY"} <= entity_types
