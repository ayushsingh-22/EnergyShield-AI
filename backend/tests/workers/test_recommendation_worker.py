from datetime import datetime, timezone

from models.core_schema import CommodityType
from models.scenario_schema import ScenarioResult, ScenarioType
from workers.recommendation_worker import run_recommendation_job


class _FakeRecommendationService:
    def __init__(self):
        self.calls = []

    def get_or_create_for_scenario(self, scenario):
        self.calls.append(scenario.scenario_id)
        return {"scenario_id": scenario.scenario_id}


def _scenario(scenario_id) -> ScenarioResult:
    return ScenarioResult(
        scenario_id=scenario_id,
        scenario_type=ScenarioType.HORMUZ_PARTIAL_CLOSURE,
        commodity_type=CommodityType.CRUDE_OIL,
        duration_days=15,
        supply_at_risk_percent=20.0,
        estimated_delay_days=5.0,
        freight_cost_impact_percent=10.0,
        affected_refineries=[],
        recommended_action_required=True,
        confidence=0.8,
        assumptions=[],
        created_at=datetime.now(timezone.utc),
    )


def test_run_recommendation_job_calls_service_for_every_scenario():
    service = _FakeRecommendationService()
    scenarios = [_scenario("SCN-1"), _scenario("SCN-2")]

    results = run_recommendation_job(scenarios, service)

    assert service.calls == ["SCN-1", "SCN-2"]
    assert len(results) == 2
