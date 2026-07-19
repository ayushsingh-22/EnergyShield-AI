"""Agent wrapper that turns procurement optimizer output into ranked alternate supplier/route recommendations."""

from __future__ import annotations

from models.recommendation_schema import ProcurementOption
from models.scenario_schema import ScenarioResult
from optimization import procurement_optimizer
from scenarios.scenario_engine import ScenarioEngine
from services.digital_twin_service import DigitalTwinService
from services.event_service import EventService

# A supplier named in a same-or-higher severity risk event is treated as
# still under active disruption and excluded from candidates (section 7.1,
# step 2), matching the severity scale `models.event_schema.RiskEvent` uses.
_HIGH_SEVERITY_THRESHOLD = 4


def _load_default_digital_twin() -> DigitalTwinService:
    digital_twin = DigitalTwinService()
    digital_twin.load_seed_data()
    return digital_twin


class ProcurementAgent:
    """Turns a scenario result into ranked procurement options (sections
    7.1, 7.2, 7.4): resolves which suppliers/routes the scenario blocks,
    finds graph-derived alternatives excluding suppliers under active
    high-severity events, and scores the survivors."""

    def __init__(
        self,
        digital_twin: DigitalTwinService | None = None,
        scenario_engine: ScenarioEngine | None = None,
        event_service: EventService | None = None,
    ):
        self._digital_twin = digital_twin or _load_default_digital_twin()
        self._scenario_engine = scenario_engine or ScenarioEngine(digital_twin=self._digital_twin)
        self._event_service = event_service

    def recommend(self, scenario: ScenarioResult) -> list[ProcurementOption]:
        resolved_entity_ids = self._scenario_engine.get_resolved_entity_ids(scenario.scenario_type)
        blocked = procurement_optimizer.find_blocked_suppliers(self._digital_twin, resolved_entity_ids)

        high_risk_entities: set[str] = set()
        if self._event_service is not None:
            for event in self._event_service.get_all():
                if event.severity >= _HIGH_SEVERITY_THRESHOLD:
                    high_risk_entities.update(event.affected_entities)

        candidates = procurement_optimizer.find_candidate_suppliers(
            self._digital_twin, scenario.commodity_type, blocked, high_risk_entities
        )
        return procurement_optimizer.rank_procurement_options(
            self._digital_twin,
            candidates,
            scenario.freight_cost_impact_percent,
            scenario.recommended_action_required,
        )
