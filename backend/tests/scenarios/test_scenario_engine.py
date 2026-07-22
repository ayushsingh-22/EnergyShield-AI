from datetime import datetime, timezone

from models.core_schema import CommodityType, RiskLevel
from models.scenario_schema import ScenarioRequest, ScenarioType
from scenarios.scenario_engine import ScenarioEngine
from services.digital_twin_service import DigitalTwinService


def _digital_twin() -> DigitalTwinService:
    twin = DigitalTwinService()
    twin.load_seed_data()
    return twin


def _request(**overrides) -> ScenarioRequest:
    defaults = dict(
        scenario_type=ScenarioType.HORMUZ_PARTIAL_CLOSURE,
        commodity_type=CommodityType.CRUDE_OIL,
        duration_days=15,
        severity=RiskLevel.HIGH,
        affected_entities=[],
        manual_overrides={},
    )
    defaults.update(overrides)
    return ScenarioRequest(**defaults)


def test_every_mvp_scenario_runs_and_returns_valid_output():
    engine = ScenarioEngine(_digital_twin())
    for scenario_type in ScenarioType:
        result = engine.run(
            _request(scenario_type=scenario_type),
            scenario_id=f"SCN-TEST-{scenario_type.value}",
            created_at=datetime.now(timezone.utc),
        )
        assert result.scenario_type == scenario_type.value
        assert 0.0 <= result.supply_at_risk_percent <= 100.0
        assert result.estimated_delay_days >= 0.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.assumptions


def test_scenario_uses_graph_relationships_not_hardcoded_refineries():
    engine = ScenarioEngine(_digital_twin())
    result = engine.run(_request(), scenario_id="SCN-TEST-1", created_at=datetime.now(timezone.utc))

    # CHK_HORMUZ transits RT_BAS_JAM (arrives PRT_JAM) and RT_RAS_MUN
    # (arrives PRT_MUN); both ports feed REF_JAM (data/seeds/refineries.csv)
    # - a real digital-twin/graph chain, not an arbitrary slice of the
    # refinery list. REF_MUM feeds only from PRT_MUM (Mumbai), which no
    # Hormuz-transiting route reaches, so it must NOT appear here - an exact
    # assertion (not a subset check) so a future regression that silently
    # drops or widens exposure is actually caught.
    refinery_ids = {refinery.refinery_id for refinery in result.affected_refineries}
    assert refinery_ids == {"REF_JAM"}
    assert all(refinery.exposure_level for refinery in result.affected_refineries)


def test_output_changes_with_severity():
    engine = ScenarioEngine(_digital_twin())
    low = engine.run(_request(severity=RiskLevel.LOW), scenario_id="SCN-LOW", created_at=datetime.now(timezone.utc))
    critical = engine.run(
        _request(severity=RiskLevel.CRITICAL), scenario_id="SCN-CRIT", created_at=datetime.now(timezone.utc)
    )
    assert critical.supply_at_risk_percent > low.supply_at_risk_percent
    assert critical.freight_cost_impact_percent > low.freight_cost_impact_percent


def test_output_changes_with_duration():
    engine = ScenarioEngine(_digital_twin())
    short = engine.run(
        _request(duration_days=2), scenario_id="SCN-SHORT", created_at=datetime.now(timezone.utc)
    )
    long = engine.run(
        _request(duration_days=60), scenario_id="SCN-LONG", created_at=datetime.now(timezone.utc)
    )
    assert long.estimated_delay_days >= short.estimated_delay_days


def test_confidence_decreases_when_manual_overrides_used():
    engine = ScenarioEngine(_digital_twin())
    baseline = engine.run(_request(), scenario_id="SCN-BASE", created_at=datetime.now(timezone.utc))
    overridden = engine.run(
        _request(manual_overrides={"supply_reduction_percent": 50.0}),
        scenario_id="SCN-OVR",
        created_at=datetime.now(timezone.utc),
    )
    assert overridden.confidence < baseline.confidence
    assert overridden.supply_at_risk_percent == 50.0


def test_partial_entity_resolution_is_disclosed_not_silent():
    """port_congestion.yaml lists JNPT, SIKKA, PARADIP - JNPT/PARADIP
    resolve to real ports but SIKKA has no seeded digital-twin entity yet.
    That gap must stay visible in assumptions even though enough of the
    template resolved to still count as "uses graph relationships."""
    engine = ScenarioEngine(_digital_twin())
    result = engine.run(
        _request(scenario_type=ScenarioType.PORT_CONGESTION),
        scenario_id="SCN-PARTIAL",
        created_at=datetime.now(timezone.utc),
    )

    assert result.affected_refineries  # JNPT/PARADIP did resolve to real exposure
    assert any("SIKKA" in assumption.description for assumption in result.assumptions)


def test_confidence_decreases_when_entities_unresolved():
    engine = ScenarioEngine(_digital_twin())
    resolved = engine.run(
        _request(scenario_type=ScenarioType.HORMUZ_PARTIAL_CLOSURE),
        scenario_id="SCN-RESOLVED",
        created_at=datetime.now(timezone.utc),
    )
    unresolved = engine.run(
        _request(scenario_type=ScenarioType.LNG_SUPPLY_SHOCK),
        scenario_id="SCN-UNRESOLVED",
        created_at=datetime.now(timezone.utc),
    )
    assert unresolved.confidence < resolved.confidence


def test_assumption_is_simulated_reflects_its_own_wording_not_hardcoded_true():
    """Regression test: every template assumption used to be tagged
    `is_simulated=True` unconditionally, even ones whose own text says
    "estimated" (real-ish directional data) rather than "simulated"
    (fabricated placeholder) - collapsing a distinction
    docs/SCENARIO_ASSUMPTIONS.md explicitly documents. coal_import_disruption
    is a good fixture because its template mixes both kinds of wording."""
    engine = ScenarioEngine(_digital_twin())
    result = engine.run(
        _request(scenario_type=ScenarioType.COAL_IMPORT_DISRUPTION, commodity_type=CommodityType.COAL),
        scenario_id="SCN-SIMULATED-FLAG",
        created_at=datetime.now(timezone.utc),
    )

    by_text = {a.description: a.is_simulated for a in result.assumptions}
    assert by_text["Import share data is estimated"] is False
    assert by_text["Exact cargo ownership is simulated"] is True
    assert by_text["Rail corridor bottleneck impact on last-mile delivery is simulated"] is True

    # Disclosures about the fallback methodology / data gaps are factual,
    # not simulated data, so they must not carry is_simulated=True either.
    fallback_disclosures = [
        a
        for a in result.assumptions
        if "could not be matched to specific digital-twin nodes" in a.description
    ]
    assert fallback_disclosures and all(a.is_simulated is False for a in fallback_disclosures)
