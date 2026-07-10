"""Stores and retrieves procurement and SPR recommendation outputs backing the recommendations API (Phase 7)."""

from __future__ import annotations

from datetime import datetime, timezone

from models.core_schema import ActionPriority, Assumption, RiskLevel
from models.recommendation_schema import ProcurementOption, Recommendation, SprPlan
from models.scenario_schema import ScenarioResult


class RecommendationService:
    def __init__(self) -> None:
        self._recommendations: dict[str, Recommendation] = {}

    def get_recommendation(self, scenario_id: str) -> Recommendation | None:
        return self._recommendations.get(scenario_id)

    def get_or_create_for_scenario(self, scenario: ScenarioResult) -> Recommendation:
        existing = self.get_recommendation(scenario.scenario_id)
        if existing is not None:
            return existing

        drawdown_required = scenario.supply_at_risk_percent >= 25 or scenario.estimated_delay_days >= 10
        recommendation = Recommendation(
            recommendation_id=f"REC-{scenario.scenario_id}",
            scenario_id=scenario.scenario_id,
            commodity_type=scenario.commodity_type,
            ranked_options=[
                ProcurementOption(
                    rank=1,
                    supplier="Saudi Arabia",
                    route="East-West corridor to west coast India",
                    estimated_delay_days=max(2.0, scenario.estimated_delay_days - 4.0),
                    cost_impact_percent=max(1.0, scenario.freight_cost_impact_percent - 3.0),
                    risk_level=RiskLevel.MEDIUM,
                    feasibility_score=0.82,
                    reason="Largest near-term alternative with strong crude substitution fit in the seeded demo set.",
                    action_priority=ActionPriority.IMMEDIATE if scenario.recommended_action_required else ActionPriority.MONITOR,
                ),
                ProcurementOption(
                    rank=2,
                    supplier="United Arab Emirates",
                    route="Murban-linked Gulf route with monitored exposure",
                    estimated_delay_days=max(3.0, scenario.estimated_delay_days - 2.0),
                    cost_impact_percent=max(2.0, scenario.freight_cost_impact_percent - 1.5),
                    risk_level=RiskLevel.MEDIUM,
                    feasibility_score=0.74,
                    reason="Good quality compatibility but still partially exposed to Gulf chokepoint conditions.",
                    action_priority=ActionPriority.CONTINGENCY,
                ),
            ],
            spr_plan=SprPlan(
                drawdown_required=drawdown_required,
                start_day=3 if drawdown_required else None,
                drawdown_percent=18.0 if drawdown_required else None,
                reason="Triggered when simulated disruption exceeds the pre-set supply-at-risk and delay thresholds." if drawdown_required else "Scenario remains manageable through procurement rerouting alone.",
            ),
            confidence=0.79,
            assumptions=[
                Assumption(description="Recommendation ranking is a deterministic heuristic using delay, cost, and route exposure.", is_simulated=True),
                Assumption(description="Supplier compatibility and SPR drawdown limits remain mocked until optimizer integration.", is_simulated=True),
            ],
            audit_id=f"AUD-REC-{scenario.scenario_id}",
            created_at=datetime.now(timezone.utc),
        )
        self._recommendations[scenario.scenario_id] = recommendation
        return recommendation
