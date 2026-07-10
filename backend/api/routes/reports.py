"""Executive crisis-response report generation endpoints (Phase 8 backend platform APIs)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.routes.recommendations import _recommendation_service
from api.routes.scenarios import service as scenario_service
from services.report_service import ReportService

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])
_report_service = ReportService()


class ReportRequest(BaseModel):
    scenario_id: str


@router.post("/generate")
def generate_report(request: ReportRequest) -> dict[str, object]:
    scenario = scenario_service.get_scenario(request.scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"Scenario '{request.scenario_id}' not found")
    recommendation = _recommendation_service.get_or_create_for_scenario(scenario)
    return _report_service.generate_report(scenario, recommendation)
