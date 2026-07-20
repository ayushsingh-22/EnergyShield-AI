import pytest

from agents.report_agent import ReportAgent, ScenarioNotFoundError
from models.core_schema import CommodityType, RiskLevel
from models.scenario_schema import ScenarioRequest, ScenarioType
from scenarios.scenario_engine import ScenarioEngine
from services.digital_twin_service import DigitalTwinService
from services.recommendation_service import RecommendationService
from services.report_service import ReportService
from services.scenario_service import ScenarioService


def _digital_twin() -> DigitalTwinService:
    service = DigitalTwinService()
    service.load_seed_data()
    return service


def _request(**overrides) -> ScenarioRequest:
    defaults = dict(
        scenario_type=ScenarioType.HORMUZ_PARTIAL_CLOSURE,
        commodity_type=CommodityType.CRUDE_OIL,
        duration_days=15,
        severity=RiskLevel.HIGH,
        affected_entities=[],
        manual_overrides={},
    )
    defaults.update(overrides)
    return ScenarioRequest(**defaults)


def _agent() -> tuple[ReportAgent, ScenarioService]:
    scenario_service = ScenarioService(engine=ScenarioEngine(_digital_twin()))
    recommendation_service = RecommendationService()
    agent = ReportAgent(
        scenario_service=scenario_service,
        recommendation_service=recommendation_service,
        report_service=ReportService(),
    )
    return agent, scenario_service


def test_draft_report_assembles_scenario_and_recommendation_into_markdown():
    agent, scenario_service = _agent()
    scenario = scenario_service.run_scenario(_request())

    report = agent.draft_report(scenario.scenario_id)

    assert report["scenario_id"] == scenario.scenario_id
    assert "report_markdown" in report
    assert scenario.scenario_type in report["report_markdown"]


def test_draft_report_unknown_scenario_raises():
    agent, _ = _agent()

    with pytest.raises(ScenarioNotFoundError):
        agent.draft_report("SCN-NEVER-RUN")


def test_get_context_returns_none_for_unknown_scenario():
    agent, _ = _agent()
    assert agent.get_context("SCN-NEVER-RUN") is None


def test_get_context_returns_scenario_and_recommendation_pair():
    agent, scenario_service = _agent()
    scenario = scenario_service.run_scenario(_request())

    context = agent.get_context(scenario.scenario_id)

    assert context is not None
    fetched_scenario, recommendation = context
    assert fetched_scenario.scenario_id == scenario.scenario_id
    assert recommendation.scenario_id == scenario.scenario_id
