"""End-to-end pipeline definitions: ingestion -> extraction -> graph update -> risk scoring -> scenario -> recommendation."""

from __future__ import annotations

import logging
from typing import Callable

from models.event_schema import RiskEvent
from models.recommendation_schema import Recommendation
from models.risk_schema import RiskScore
from models.scenario_schema import ScenarioResult
from orchestration.event_bus import EventBus, get_event_bus
from orchestration.job_status import JobStatusTracker, get_job_status_tracker
from services.audit_service import AuditService
from services.recommendation_service import RecommendationService
from services.risk_service import RiskService
from services.scenario_service import ScenarioService
from workers import recommendation_worker, risk_worker, scenario_worker

logger = logging.getLogger(__name__)


def _default_extraction_pipeline() -> list[RiskEvent]:
    from api.routes.events import run_extraction_pipeline

    return run_extraction_pipeline()


def _default_risk_service() -> RiskService:
    from api.routes.risk import get_risk_service

    return get_risk_service()


def _default_scenario_service() -> ScenarioService:
    from api.routes.scenarios import service

    return service


def _default_recommendation_service() -> RecommendationService:
    from api.routes.recommendations import get_recommendation_service

    return get_recommendation_service()


def _default_audit_service() -> AuditService:
    from api.routes.audit import get_audit_service

    return get_audit_service()


def run_full_pipeline(
    *,
    extraction_pipeline: Callable[[], list[RiskEvent]] | None = None,
    risk_service: RiskService | None = None,
    scenario_service: ScenarioService | None = None,
    recommendation_service: RecommendationService | None = None,
    audit_service: AuditService | None = None,
    event_bus: EventBus | None = None,
    job_status_tracker: JobStatusTracker | None = None,
) -> dict[str, object]:
    """Runs the Phase 10 main workflow once, end to end:

        collector run -> normalized signals -> event extraction
        -> entity resolution / graph update -> risk scoring
        -> scenario auto-trigger (10.4) -> recommendation generation
        -> audit trail at each step

    Every dependency defaults to the live route-module singleton (so
    calling this with no arguments - from the scheduler or a manual
    trigger - wires up the real pipeline) but can be overridden, so tests
    can exercise the orchestration logic without a live LLM/Neo4j/Postgres.
    """
    extraction_pipeline = extraction_pipeline or _default_extraction_pipeline
    risk_service = risk_service or _default_risk_service()
    scenario_service = scenario_service or _default_scenario_service()
    recommendation_service = recommendation_service or _default_recommendation_service()
    audit_service = audit_service or _default_audit_service()
    bus = event_bus or get_event_bus()
    tracker = job_status_tracker or get_job_status_tracker()

    run = tracker.start("full_pipeline")
    summary: dict[str, object] = {"events_extracted": 0, "triggered_scenario_ids": []}

    try:
        # 10.1 + 10.2: scheduled data refresh and event-driven extraction
        # (also performs the Phase 3 graph update as a side effect).
        events = extraction_pipeline()
        summary["events_extracted"] = len(events)
        bus.publish("events.extracted", {"count": len(events)})

        # 10.3: risk (and graph) update.
        scores: list[RiskScore] = risk_worker.run_risk_scoring_job(risk_service)
        bus.publish("risk.updated", {"scored_entities": len(scores)})

        # 10.4: scenario auto-trigger when risk crosses threshold.
        triggered_scenarios: list[ScenarioResult] = scenario_worker.run_scenario_trigger_job(
            scores, scenario_service
        )
        for scenario in triggered_scenarios:
            bus.publish("scenario.triggered", {"scenario_id": scenario.scenario_id})
            audit_service.record_event(
                entity_id=scenario.scenario_id,
                entity_type="SCENARIO",
                action="AUTO_TRIGGERED",
                summary=f"Auto-triggered scenario {scenario.scenario_type} from a risk score crossing threshold.",
            )
        summary["triggered_scenario_ids"] = [s.scenario_id for s in triggered_scenarios]

        # Recommendation generation for every auto-triggered scenario.
        recommendations: list[Recommendation] = recommendation_worker.run_recommendation_job(
            triggered_scenarios, recommendation_service
        )
        for recommendation in recommendations:
            bus.publish("recommendation.generated", {"recommendation_id": recommendation.recommendation_id})
        summary["recommendation_ids"] = [r.recommendation_id for r in recommendations]

        tracker.finish(run, details=summary)
    except Exception as exc:  # noqa: BLE001 - a failed pipeline run must not crash the scheduler/caller
        logger.exception("Full pipeline run failed")
        tracker.finish(run, error=str(exc))
        audit_service.record_event(
            entity_id=run.run_id,
            entity_type="PIPELINE_RUN",
            action="PIPELINE_FAILED",
            summary=f"Pipeline run failed: {exc}",
        )

    return summary
