"""Executive report generation backing the reports API (Phase 8)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from models.recommendation_schema import Recommendation
from models.scenario_schema import ScenarioResult
from reports.formatting import humanize
from reports.report_builder import build_markdown_report
from services.audit_service import AuditService
from services.digital_twin_service import DigitalTwinService
from storage import repository


def _load_default_digital_twin() -> DigitalTwinService:
    digital_twin = DigitalTwinService()
    digital_twin.load_seed_data()
    return digital_twin


class ReportService:
    def __init__(
        self, audit_service: AuditService | None = None, digital_twin: DigitalTwinService | None = None
    ) -> None:
        self._audit_service = audit_service
        self._digital_twin = digital_twin or _load_default_digital_twin()

    def generate_report(self, scenario: ScenarioResult, recommendation: Recommendation) -> dict[str, object]:
        generated_at = datetime.now(timezone.utc)
        report_id = f"RPT-{scenario.scenario_id}"
        markdown = build_markdown_report(
            report_id=report_id,
            generated_at=generated_at,
            scenario=scenario,
            recommendation=recommendation,
            digital_twin=self._digital_twin,
        )

        audit_id = recommendation.audit_id
        if self._audit_service is not None:
            audit_event = self._audit_service.record_event(
                entity_id=report_id,
                entity_type="REPORT",
                action="REPORT_GENERATED",
                summary=f"Generated executive brief for {scenario.scenario_id}.",
                details={"recommendation_id": recommendation.recommendation_id},
            )
            audit_id = audit_event.audit_id

        report = {
            "report_id": report_id,
            "generated_at": generated_at,
            "scenario_id": scenario.scenario_id,
            "recommendation_id": recommendation.recommendation_id,
            "title": f"EnergyShield Executive Brief - {humanize(scenario.scenario_type)}",
            "executive_summary": (
                f"{humanize(scenario.commodity_type)} disruption scenario {humanize(scenario.scenario_type)} places "
                f"{scenario.supply_at_risk_percent}% of supply at risk with an estimated "
                f"{scenario.estimated_delay_days}-day delay."
            ),
            "report_markdown": markdown,
            "top_actions": [option.reason for option in recommendation.ranked_options[:2]],
            "spr_action": recommendation.spr_plan.model_dump() if recommendation.spr_plan else None,
            "audit_id": audit_id,
            "assumptions": [
                assumption.model_dump() for assumption in scenario.assumptions + recommendation.assumptions
            ],
            "is_simulated": True,
        }
        repository.save_generated_report(report_id, scenario.scenario_id, json.dumps(report, default=str))
        return report
