"""Agent wrapper that turns SPR optimizer output into strategic reserve drawdown recommendations."""

from __future__ import annotations

from models.core_schema import RiskLevel
from models.recommendation_schema import SprPlan
from models.scenario_schema import ScenarioResult
from optimization import spr_optimizer
from services.digital_twin_service import DigitalTwinService

_RISK_LEVEL_ORDER = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.SEVERE, RiskLevel.CRITICAL]


def _load_default_digital_twin() -> DigitalTwinService:
    digital_twin = DigitalTwinService()
    digital_twin.load_seed_data()
    return digital_twin


def _infer_severity(scenario: ScenarioResult) -> RiskLevel:
    """`ScenarioResult` doesn't carry the original request's `severity`
    field, so the SPR plan infers an equivalent from the scenario's own
    graph-derived output: the highest `exposure_level` among its affected
    refineries when any resolved, otherwise a threshold on
    `supply_at_risk_percent`."""
    if scenario.affected_refineries:
        return max((r.exposure_level for r in scenario.affected_refineries), key=_RISK_LEVEL_ORDER.index)
    percent = scenario.supply_at_risk_percent
    if percent >= 40:
        return RiskLevel.CRITICAL
    if percent >= 25:
        return RiskLevel.SEVERE
    if percent >= 15:
        return RiskLevel.HIGH
    if percent >= 5:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


class SprAgent:
    """Turns a scenario result into a strategic reserve drawdown
    recommendation (section 7.3)."""

    def __init__(self, digital_twin: DigitalTwinService | None = None):
        self._digital_twin = digital_twin or _load_default_digital_twin()

    def recommend(self, scenario: ScenarioResult) -> SprPlan:
        return spr_optimizer.recommend_spr_plan(
            supply_at_risk_percent=scenario.supply_at_risk_percent,
            estimated_delay_days=scenario.estimated_delay_days,
            duration_days=scenario.duration_days,
            severity=_infer_severity(scenario),
            digital_twin=self._digital_twin,
        )
