"""Scenario run and history endpoints (Phase 6 disruption scenario modeller)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from models.scenario_schema import ScenarioRequest, ScenarioResult
from services.scenario_service import ScenarioService

router = APIRouter(prefix="/api/v1/scenarios", tags=["scenarios"])
service = ScenarioService()


@router.post("/run", response_model=ScenarioResult)
def run_scenario(request: ScenarioRequest) -> ScenarioResult:
    return service.run_scenario(request)


@router.get("/{scenario_id}", response_model=ScenarioResult)
def get_scenario(scenario_id: str) -> ScenarioResult:
    result = service.get_scenario(scenario_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    return result
