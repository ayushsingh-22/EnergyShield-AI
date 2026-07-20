"""Agent wrapper that assembles event, risk, scenario, and recommendation context into an executive report draft."""

from __future__ import annotations

from models.recommendation_schema import Recommendation
from models.scenario_schema import ScenarioResult
from services.recommendation_service import RecommendationService
from services.report_service import ReportService
from services.scenario_service import ScenarioService


class ScenarioNotFoundError(Exception):
    """Raised when the report agent is asked to draft a report for a scenario_id that no ScenarioService has on record."""


class ReportAgent:
    """Owns the section 8.3 assembly step end to end: given only a
    `scenario_id`, looks up the Phase 6 scenario result, gets or generates
    its Phase 7 recommendation, and hands both to `ReportService` for
    rendering - the same lookup chain `api/routes/reports.py` previously
    performed inline."""

    def __init__(
        self,
        scenario_service: ScenarioService,
        recommendation_service: RecommendationService,
        report_service: ReportService | None = None,
    ):
        self._scenario_service = scenario_service
        self._recommendation_service = recommendation_service
        self._report_service = report_service or ReportService()

    def draft_report(self, scenario_id: str) -> dict[str, object]:
        scenario = self._scenario_service.get_scenario(scenario_id)
        if scenario is None:
            raise ScenarioNotFoundError(f"Scenario '{scenario_id}' not found")
        recommendation = self._recommendation_service.get_or_create_for_scenario(scenario)
        return self._report_service.generate_report(scenario, recommendation)

    def get_context(self, scenario_id: str) -> tuple[ScenarioResult, Recommendation] | None:
        """Returns the raw (scenario, recommendation) pair a caller wants to
        inspect directly (e.g. a future evaluation or dashboard view)
        without re-rendering the Markdown report."""
        scenario = self._scenario_service.get_scenario(scenario_id)
        if scenario is None:
            return None
        recommendation = self._recommendation_service.get_or_create_for_scenario(scenario)
        return scenario, recommendation
