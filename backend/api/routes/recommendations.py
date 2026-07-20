"""Procurement and SPR recommendation endpoints (Phase 7 adaptive procurement and SPR agents)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from agents.procurement_agent import ProcurementAgent
from api.routes.audit import get_audit_service
from api.routes.events import get_event_service
from api.routes.scenarios import service as scenario_service
from models.recommendation_schema import Recommendation
from services.recommendation_service import RecommendationService

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])
# Wires the live Phase 4 event feed into the Phase 7 procurement agent so
# candidate suppliers currently under an active high-severity event are
# excluded, same pattern `api/routes/risk.py` uses for Phase 5.
_recommendation_service = RecommendationService(
    procurement_agent=ProcurementAgent(event_service=get_event_service()),
    audit_service=get_audit_service(),
)


@router.get("/{scenario_id}", response_model=Recommendation)
def get_recommendation(scenario_id: str) -> Recommendation:
    scenario = scenario_service.get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    return _recommendation_service.get_or_create_for_scenario(scenario)


def get_recommendation_service() -> RecommendationService:
    """Exposes the module-level `RecommendationService` singleton so
    Phase 10's orchestration workflow can generate recommendations for an
    auto-triggered scenario through the same service this router serves."""
    return _recommendation_service
