"""Recommendation generation jobs (Phase 10 main workflow: "procurement and SPR agents generate recommendations")."""

from __future__ import annotations

from models.recommendation_schema import Recommendation
from models.scenario_schema import ScenarioResult
from services.recommendation_service import RecommendationService


def run_recommendation_job(
    scenarios: list[ScenarioResult], recommendation_service: RecommendationService
) -> list[Recommendation]:
    return [recommendation_service.get_or_create_for_scenario(scenario) for scenario in scenarios]
