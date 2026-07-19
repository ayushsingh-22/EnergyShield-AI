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

    # CHK_HORMUZ transits RT_BAS_JAM/RT_RAS_MUN, which arrive at PRT_JAM/PRT_MUN,
    # which feed REF_JAM/REF_MUM respectively - a real digital-twin/graph chain,
    # not an arbitrary slice of the refinery list.
    refinery_ids = {refinery.refinery_id for refinery in result.affected_refineries}
    assert refinery_ids
    assert refinery_ids.issubset({"REF_JAM", "REF_MUM"})


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
