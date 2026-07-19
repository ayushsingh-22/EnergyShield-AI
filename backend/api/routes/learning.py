"""Historical case library, backtest, feedback, and model version endpoints
(Phase 13 continuous learning from past disruptions).

See docs/API_REFERENCE.md for the endpoints this router owns.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from learning.backtesting import BacktestReport, run_backtest
from learning.disruption_case_library import DisruptionCaseLibrary
from learning.feedback_service import FeedbackService
from learning.model_registry import ModelRegistry
from models.learning_schema import FeedbackAction, FeedbackEntry, HistoricalCase, ModelVersion

router = APIRouter(prefix="/api/v1/learning", tags=["learning"])

_case_library = DisruptionCaseLibrary()
_case_library.load_seed_data()
_feedback_service = FeedbackService()
_model_registry = ModelRegistry()
_backtest_runs: dict[str, BacktestReport] = {}


class FeedbackRequest(BaseModel):
    recommendation_id: str
    useful: bool
    action_taken: FeedbackAction
    rejection_reason: str | None = None
    submitted_by: str | None = None


class BacktestRequest(BaseModel):
    case_ids: list[str] | None = None
    flag_threshold_percent: float = 15.0


@router.get("/cases", response_model=list[HistoricalCase])
def list_cases() -> list[HistoricalCase]:
    return _case_library.get_all()


@router.get("/cases/{case_id}", response_model=HistoricalCase)
def get_case(case_id: str) -> HistoricalCase:
    case = _case_library.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail=f"Historical case '{case_id}' not found")
    return case


@router.post("/backtest")
def run_backtest_endpoint(request: BacktestRequest) -> dict[str, object]:
    cases = _case_library.get_all()
    if request.case_ids:
        cases = [case for case in cases if case.case_id in request.case_ids]
    report = run_backtest(cases, flag_threshold_percent=request.flag_threshold_percent)
    _backtest_runs[report.run_id] = report
    return _serialize_report(report)


@router.get("/backtest/{run_id}")
def get_backtest_run(run_id: str) -> dict[str, object]:
    report = _backtest_runs.get(run_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Backtest run '{run_id}' not found")
    return _serialize_report(report)


@router.post("/feedback", response_model=FeedbackEntry)
def submit_feedback(request: FeedbackRequest) -> FeedbackEntry:
    return _feedback_service.submit_feedback(
        recommendation_id=request.recommendation_id,
        useful=request.useful,
        action_taken=request.action_taken,
        rejection_reason=request.rejection_reason,
        submitted_by=request.submitted_by,
    )


@router.get("/models", response_model=list[ModelVersion])
def list_models() -> list[ModelVersion]:
    return _model_registry.list_all()


@router.post("/models/{model_id}/activate", response_model=ModelVersion)
def activate_model(model_id: str) -> ModelVersion:
    try:
        return _model_registry.activate(model_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _serialize_report(report: BacktestReport) -> dict[str, object]:
    return {
        "run_id": report.run_id,
        "precision": report.precision,
        "recall": report.recall,
        "false_alarm_rate": report.false_alarm_rate,
        "missed_event_rate": report.missed_event_rate,
        "case_results": [
            {
                "case_id": result.case_id,
                "scenario_type": result.scenario_type,
                "predicted_materially_disruptive": result.predicted_materially_disruptive,
                "observed_materially_disruptive": result.observed_materially_disruptive,
                "predicted_supply_at_risk_percent": result.predicted_supply_at_risk_percent,
                "predicted_confidence": result.predicted_confidence,
            }
            for result in report.case_results
        ],
    }


def get_case_library() -> DisruptionCaseLibrary:
    return _case_library


def get_feedback_service() -> FeedbackService:
    return _feedback_service


def get_model_registry() -> ModelRegistry:
    return _model_registry
