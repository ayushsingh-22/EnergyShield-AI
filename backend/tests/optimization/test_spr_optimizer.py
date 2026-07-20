from models.core_schema import RiskLevel
from optimization import spr_optimizer


def test_no_drawdown_for_small_low_severity_shock():
    plan = spr_optimizer.recommend_spr_plan(
        supply_at_risk_percent=4.0, estimated_delay_days=2.0, duration_days=5, severity=RiskLevel.LOW
    )
    assert plan.drawdown_required is False
    assert plan.start_day is None
    assert plan.drawdown_percent is None


def test_controlled_drawdown_for_persistent_supply_gap():
    plan = spr_optimizer.recommend_spr_plan(
        supply_at_risk_percent=20.0, estimated_delay_days=8.0, duration_days=15, severity=RiskLevel.HIGH
    )
    assert plan.drawdown_required is True
    assert plan.start_day is not None
    assert 0 < plan.drawdown_percent < 30


def test_emergency_drawdown_for_severe_extended_duration():
    plan = spr_optimizer.recommend_spr_plan(
        supply_at_risk_percent=45.0, estimated_delay_days=20.0, duration_days=90, severity=RiskLevel.CRITICAL
    )
    assert plan.drawdown_required is True
    assert plan.start_day == 1
    assert plan.drawdown_percent >= 20
