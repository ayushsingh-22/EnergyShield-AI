"""Scenario assumption completeness and output validation checks."""

from __future__ import annotations

from evaluation.backtest_metrics import percent_matching
from models.scenario_schema import ScenarioResult


def validate_scenario_result(result: ScenarioResult) -> list[str]:
    """Returns validation problems for one scenario output (empty list =
    passes). Covers the parts of the Phase 6 validation checklist that
    are checkable purely from the output object itself: assumptions
    present, confidence and percentages in range, and delay not exceeding
    the modelled disruption duration."""
    problems = []
    if not result.assumptions:
        problems.append("No assumptions attached to scenario output.")
    if not (0.0 <= result.confidence <= 1.0):
        problems.append(f"Confidence {result.confidence} outside [0, 1].")
    if not (0.0 <= result.supply_at_risk_percent <= 100.0):
        problems.append(f"supply_at_risk_percent {result.supply_at_risk_percent} outside [0, 100].")
    if result.estimated_delay_days > result.duration_days:
        problems.append("estimated_delay_days exceeds duration_days.")
    return problems


def scenario_fidelity_percent(results: list[ScenarioResult]) -> float:
    """Percentage of scenario runs with zero validation problems (Phase 11
    Evaluation Metrics table: "Scenario fidelity: all assumptions explicit
    and testable")."""
    return percent_matching(results, lambda result: not validate_scenario_result(result))
