from datetime import datetime, timezone

from evaluation.scenario_eval import scenario_fidelity_percent, validate_scenario_result
from models.core_schema import Assumption, CommodityType
from models.scenario_schema import ScenarioResult, ScenarioType


def _result(**overrides) -> ScenarioResult:
    defaults = dict(
        scenario_id="SCN-1",
        scenario_type=ScenarioType.HORMUZ_PARTIAL_CLOSURE,
        commodity_type=CommodityType.CRUDE_OIL,
        duration_days=15,
        supply_at_risk_percent=20.0,
        estimated_delay_days=5.0,
        freight_cost_impact_percent=10.0,
        fuel_price_increase_percent=8.0,
        gdp_impact_percent=0.3,
        affected_refineries=[],
        recommended_action_required=True,
        confidence=0.8,
        assumptions=[Assumption(description="x")],
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return ScenarioResult(**defaults)


def test_valid_scenario_has_no_problems():
    assert validate_scenario_result(_result()) == []


def test_missing_assumptions_is_a_problem():
    problems = validate_scenario_result(_result(assumptions=[]))
    assert any("assumption" in p.lower() for p in problems)


def test_delay_exceeding_duration_is_a_problem():
    problems = validate_scenario_result(_result(duration_days=3, estimated_delay_days=10.0))
    assert any("estimated_delay_days" in p for p in problems)


def test_scenario_fidelity_percent_counts_only_valid_results():
    valid = _result()
    invalid = _result(scenario_id="SCN-2", assumptions=[])
    assert scenario_fidelity_percent([valid, invalid]) == 50.0
    assert scenario_fidelity_percent([valid, valid]) == 100.0
