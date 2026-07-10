"""Executive report generation backing the reports API (Phase 8)."""

from __future__ import annotations

from datetime import datetime, timezone

from models.recommendation_schema import Recommendation
from models.scenario_schema import ScenarioResult


class ReportService:
    def generate_report(self, scenario: ScenarioResult, recommendation: Recommendation) -> dict[str, object]:
        generated_at = datetime.now(timezone.utc)
        return {
            "report_id": f"RPT-{scenario.scenario_id}",
            "generated_at": generated_at,
            "scenario_id": scenario.scenario_id,
            "recommendation_id": recommendation.recommendation_id,
            "title": f"EnergyShield Executive Brief - {scenario.scenario_type}",
            "executive_summary": (
                f"{scenario.commodity_type} disruption scenario {scenario.scenario_type} places "
                f"{scenario.supply_at_risk_percent}% of supply at risk with an estimated "
                f"{scenario.estimated_delay_days}-day delay."
            ),
            "top_actions": [option.reason for option in recommendation.ranked_options[:2]],
            "spr_action": recommendation.spr_plan.model_dump() if recommendation.spr_plan else None,
            "audit_id": recommendation.audit_id,
            "assumptions": [assumption.model_dump() for assumption in scenario.assumptions + recommendation.assumptions],
            "is_simulated": True,
        }
