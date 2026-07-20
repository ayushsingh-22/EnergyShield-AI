from datetime import datetime, timezone

from models.core_schema import ActionPriority, CommodityType, EntityType, RiskLevel
from models.recommendation_schema import Recommendation
from models.risk_schema import RiskScore
from models.scenario_schema import ScenarioResult, ScenarioType
from orchestration.event_bus import EventBus
from orchestration.job_status import JobStatus, JobStatusTracker
from orchestration.workflows import run_full_pipeline
from services.audit_service import AuditService


class _FakeRiskService:
    def __init__(self, scores):
        self._scores = scores
        self.refreshed = False

    def refresh(self):
        self.refreshed = True

    def get_corridors(self):
        return [s for s in self._scores if s.entity_type == EntityType.CHOKEPOINT]

    def get_suppliers(self):
        return [s for s in self._scores if s.entity_type == EntityType.SUPPLIER_COUNTRY]


class _FakeScenarioService:
    def __init__(self):
        self.run_requests = []

    def run_scenario(self, request):
        self.run_requests.append(request)
        return ScenarioResult(
            scenario_id=f"SCN-{len(self.run_requests)}",
            scenario_type=request.scenario_type,
            commodity_type=request.commodity_type,
            duration_days=request.duration_days,
            supply_at_risk_percent=30.0,
            estimated_delay_days=5.0,
            freight_cost_impact_percent=10.0,
            affected_refineries=[],
            recommended_action_required=True,
            confidence=0.8,
            assumptions=[],
            created_at=datetime.now(timezone.utc),
        )


class _FakeRecommendationService:
    def __init__(self):
        self.calls = []

    def get_or_create_for_scenario(self, scenario):
        self.calls.append(scenario.scenario_id)
        return Recommendation(
            recommendation_id=f"REC-{scenario.scenario_id}",
            scenario_id=scenario.scenario_id,
            commodity_type=scenario.commodity_type,
            ranked_options=[],
            spr_plan=None,
            confidence=0.7,
            assumptions=[],
            audit_id="AUD-1",
            created_at=datetime.now(timezone.utc),
        )


def _score(entity_id, entity_type, risk_score) -> RiskScore:
    return RiskScore(
        entity_id=entity_id,
        entity_type=entity_type,
        commodity_type=CommodityType.CRUDE_OIL,
        risk_score=risk_score,
        risk_level=RiskLevel.HIGH,
        confidence=0.8,
        updated_at=datetime.now(timezone.utc),
    )


def test_full_pipeline_triggers_scenario_and_recommendation_above_threshold():
    high_risk_score = _score("CHK_HORMUZ", EntityType.CHOKEPOINT, 85.0)
    scenario_service = _FakeScenarioService()
    recommendation_service = _FakeRecommendationService()
    audit_service = AuditService()
    tracker = JobStatusTracker()
    bus = EventBus(redis_url="redis://nonexistent-host:6399/0")

    summary = run_full_pipeline(
        extraction_pipeline=lambda: [],
        risk_service=_FakeRiskService([high_risk_score]),
        scenario_service=scenario_service,
        recommendation_service=recommendation_service,
        audit_service=audit_service,
        event_bus=bus,
        job_status_tracker=tracker,
    )

    assert len(scenario_service.run_requests) == 1
    assert scenario_service.run_requests[0].scenario_type == ScenarioType.HORMUZ_PARTIAL_CLOSURE
    assert len(recommendation_service.calls) == 1
    assert summary["triggered_scenario_ids"] == recommendation_service.calls
    assert tracker.latest("full_pipeline").status == JobStatus.SUCCESS

    # Audit trail captures the auto-trigger step (Phase 10 validation:
    # "audit trail captures each step").
    scenario_id = summary["triggered_scenario_ids"][0]
    audit_entries = audit_service.get_events_for_entity(scenario_id)
    assert any(entry.action == "AUTO_TRIGGERED" for entry in audit_entries)


def test_full_pipeline_does_not_trigger_below_threshold():
    low_risk_score = _score("CHK_HORMUZ", EntityType.CHOKEPOINT, 40.0)
    scenario_service = _FakeScenarioService()

    summary = run_full_pipeline(
        extraction_pipeline=lambda: [],
        risk_service=_FakeRiskService([low_risk_score]),
        scenario_service=scenario_service,
        recommendation_service=_FakeRecommendationService(),
        audit_service=AuditService(),
        event_bus=EventBus(redis_url="redis://nonexistent-host:6399/0"),
        job_status_tracker=JobStatusTracker(),
    )

    assert scenario_service.run_requests == []
    assert summary["triggered_scenario_ids"] == []


def test_full_pipeline_records_failure_without_raising():
    tracker = JobStatusTracker()

    def _failing_extraction():
        raise RuntimeError("collector exploded")

    summary = run_full_pipeline(
        extraction_pipeline=_failing_extraction,
        risk_service=_FakeRiskService([]),
        scenario_service=_FakeScenarioService(),
        recommendation_service=_FakeRecommendationService(),
        audit_service=AuditService(),
        event_bus=EventBus(redis_url="redis://nonexistent-host:6399/0"),
        job_status_tracker=tracker,
    )

    assert tracker.latest("full_pipeline").status == JobStatus.FAILED
    assert "collector exploded" in tracker.latest("full_pipeline").error
