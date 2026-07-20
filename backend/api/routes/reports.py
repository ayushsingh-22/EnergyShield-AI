"""Executive crisis-response report generation endpoints (Phase 8 backend platform APIs)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.report_agent import ReportAgent, ScenarioNotFoundError
from api.routes.audit import get_audit_service
from api.routes.recommendations import _recommendation_service
from api.routes.scenarios import service as scenario_service
from services.report_service import ReportService

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])
_report_service = ReportService(audit_service=get_audit_service())
_report_agent = ReportAgent(
    scenario_service=scenario_service,
    recommendation_service=_recommendation_service,
    report_service=_report_service,
)


class ReportRequest(BaseModel):
    scenario_id: str


@router.post("/generate")
def generate_report(request: ReportRequest) -> dict[str, object]:
    try:
        return _report_agent.draft_report(request.scenario_id)
    except ScenarioNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
