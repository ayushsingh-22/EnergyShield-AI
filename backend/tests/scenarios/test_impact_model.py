from models.core_schema import RiskLevel
from scenarios import impact_model


def test_compute_supply_at_risk_percent_override_clamped_to_range():
    result = impact_model.compute_supply_at_risk_percent((10, 35), RiskLevel.HIGH, {"supply_reduction_percent": 500}, [])
    assert result == 100.0


def test_compute_freight_cost_impact_percent_override_capped():
    """Regression test: a large manual override used to sail straight
    through with no upper bound, unlike supply_at_risk_percent's Field(le=100)."""
    overrides_used = []
    result = impact_model.compute_freight_cost_impact_percent(
        (8, 25), RiskLevel.HIGH, {"freight_cost_increase_percent": 99999}, overrides_used
    )
    assert result == impact_model._MAX_FREIGHT_COST_IMPACT_PERCENT
    assert overrides_used == ["freight_cost_increase_percent"]


def test_compute_freight_cost_impact_percent_negative_override_floored_at_zero():
    result = impact_model.compute_freight_cost_impact_percent((8, 25), RiskLevel.HIGH, {"freight_cost_increase_percent": -50}, [])
    assert result == 0.0


def test_compute_freight_cost_impact_percent_scales_with_severity_without_override():
    low = impact_model.compute_freight_cost_impact_percent((8, 25), RiskLevel.LOW, {}, [])
    critical = impact_model.compute_freight_cost_impact_percent((8, 25), RiskLevel.CRITICAL, {}, [])
    assert critical > low
    assert critical <= impact_model._MAX_FREIGHT_COST_IMPACT_PERCENT


def test_compute_estimated_delay_days_capped_at_duration():
    delay = impact_model.compute_estimated_delay_days(
        default_duration_days=15,
        duration_days=5,
        severity=RiskLevel.CRITICAL,
        affected_route_transit_days=[30.0, 40.0],
        manual_overrides={},
        overrides_used=[],
    )
    assert delay <= 5.0


def test_compute_confidence_clamped_between_bounds():
    all_discounts = impact_model.compute_confidence(
        manual_overrides_used=["supply_reduction_percent"],
        resolved_specific_entities=False,
        duration_days=100,
        default_duration_days=15,
        stale_baseline=True,
    )
    no_discounts = impact_model.compute_confidence(
        manual_overrides_used=[],
        resolved_specific_entities=True,
        duration_days=15,
        default_duration_days=15,
        stale_baseline=False,
    )
    assert 0.4 <= all_discounts < no_discounts <= 0.95
