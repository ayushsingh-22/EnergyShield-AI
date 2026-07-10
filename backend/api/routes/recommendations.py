"""Procurement and SPR recommendation endpoints (Phase 7 adaptive procurement and SPR agents)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.routes.scenarios import service as scenario_service
from models.recommendation_schema import Recommendation
from services.recommendation_service import RecommendationService

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])
_recommendation_service = RecommendationService()


@router.get("/{scenario_id}", response_model=Recommendation)
def get_recommendation(scenario_id: str) -> Recommendation:
    scenario = scenario_service.get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    return _recommendation_service.get_or_create_for_scenario(scenario)
