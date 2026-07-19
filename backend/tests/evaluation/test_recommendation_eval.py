from datetime import datetime, timezone

from evaluation.recommendation_eval import (
    auditability_percent,
    has_audit_trail,
    has_complete_option_fields,
    recommendation_quality_percent,
)
from models.core_schema import ActionPriority, CommodityType, RiskLevel
from models.recommendation_schema import ProcurementOption, Recommendation


def _option(**overrides) -> ProcurementOption:
    defaults = dict(
        rank=1,
        supplier="Iraq",
        route="Basra to Jamnagar",
        estimated_delay_days=4.0,
        cost_impact_percent=5.0,
        risk_level=RiskLevel.MEDIUM,
        feasibility_score=0.8,
        reason="test",
        action_priority=ActionPriority.MONITOR,
    )
    defaults.update(overrides)
    return ProcurementOption(**defaults)


def _recommendation(**overrides) -> Recommendation:
    defaults = dict(
        recommendation_id="REC-1",
        scenario_id="SCN-1",
        commodity_type=CommodityType.CRUDE_OIL,
        ranked_options=[_option()],
        spr_plan=None,
        confidence=0.8,
        assumptions=[],
        audit_id="AUD-1",
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return Recommendation(**defaults)


def test_complete_recommendation_passes():
    assert has_complete_option_fields(_recommendation()) is True


def test_recommendation_without_audit_id_fails_auditability():
    assert has_audit_trail(_recommendation(audit_id=None)) is False


def test_recommendation_quality_percent_and_auditability_percent():
    good = _recommendation()
    no_audit = _recommendation(recommendation_id="REC-2", audit_id=None)
    assert recommendation_quality_percent([good, no_audit]) == 100.0
    assert auditability_percent([good, no_audit]) == 50.0
