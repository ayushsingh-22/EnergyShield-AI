"""Stores and retrieves procurement and SPR recommendation outputs backing the recommendations API (Phase 7)."""

from __future__ import annotations

from datetime import datetime, timezone

from agents.procurement_agent import ProcurementAgent
from agents.spr_agent import SprAgent
from models.core_schema import Assumption
from models.recommendation_schema import Recommendation
from models.scenario_schema import ScenarioResult
from services.audit_service import AuditService
from storage import repository


class RecommendationService:
    def __init__(
        self,
        procurement_agent: ProcurementAgent | None = None,
        spr_agent: SprAgent | None = None,
        audit_service: AuditService | None = None,
    ) -> None:
        self._recommendations: dict[str, Recommendation] = {}
        self._procurement_agent = procurement_agent or ProcurementAgent()
        self._spr_agent = spr_agent or SprAgent()
        self._audit_service = audit_service

    def get_recommendation(self, scenario_id: str) -> Recommendation | None:
        return self._recommendations.get(scenario_id)

    def get_or_create_for_scenario(self, scenario: ScenarioResult) -> Recommendation:
        existing = self.get_recommendation(scenario.scenario_id)
        if existing is not None:
            return existing

        ranked_options = self._procurement_agent.recommend(scenario)
        spr_plan = self._spr_agent.recommend(scenario)

        assumptions = [
            Assumption(
                description="Procurement ranking uses the Phase 7 scoring formula over digital-twin/graph data.",
                is_simulated=False,
            ),
            Assumption(
                description=(
                    "Exact tanker availability, cargo ownership, and refinery-grade compatibility "
                    "remain simulated pending live contract data."
                ),
                is_simulated=True,
            ),
        ]
        if not ranked_options:
            assumptions.append(
                Assumption(
                    description="No alternative suppliers could be resolved from the digital twin or graph for this scenario.",
                    is_simulated=True,
                )
            )

        # Recommendation confidence is capped by the scenario's own
        # confidence (a recommendation can't be more certain than the
        # scenario it's based on) and by how feasible the ranked options
        # actually are.
        option_feasibility = (
            sum(option.feasibility_score for option in ranked_options) / len(ranked_options)
            if ranked_options
            else 0.5
        )
        confidence = round(min(scenario.confidence, option_feasibility), 2)
        recommendation_id = f"REC-{scenario.scenario_id}"

        audit_id = f"AUD-REC-{scenario.scenario_id}"
        if self._audit_service is not None:
            audit_event = self._audit_service.record_event(
                entity_id=recommendation_id,
                entity_type="RECOMMENDATION",
                action="RECOMMENDATION_GENERATED",
                summary=f"Generated {len(ranked_options)} procurement option(s) for {scenario.scenario_id}.",
                details={"confidence": confidence, "spr_drawdown_required": spr_plan.drawdown_required},
            )
            audit_id = audit_event.audit_id

        recommendation = Recommendation(
            recommendation_id=recommendation_id,
            scenario_id=scenario.scenario_id,
            commodity_type=scenario.commodity_type,
            ranked_options=ranked_options,
            spr_plan=spr_plan,
            confidence=confidence,
            assumptions=assumptions,
            audit_id=audit_id,
            created_at=datetime.now(timezone.utc),
        )
        self._recommendations[scenario.scenario_id] = recommendation
        repository.save_recommendation(recommendation.recommendation_id, scenario.scenario_id, recommendation.model_dump_json())
        return recommendation
