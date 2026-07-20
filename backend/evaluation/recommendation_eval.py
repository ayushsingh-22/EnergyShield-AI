"""Recommendation quality checks: cost, risk, delay, feasibility, and confidence coverage."""

from __future__ import annotations

from evaluation.backtest_metrics import percent_matching
from models.recommendation_schema import Recommendation


def has_complete_option_fields(recommendation: Recommendation) -> bool:
    """Every ranked option carries cost, risk, delay, and feasibility, and
    the recommendation itself has a confidence score (Phase 11 Evaluation
    Metrics table: "Recommendation quality")."""
    if not (0.0 <= recommendation.confidence <= 1.0):
        return False
    return all(
        option.cost_impact_percent is not None
        and option.risk_level is not None
        and option.estimated_delay_days is not None
        and 0.0 <= option.feasibility_score <= 1.0
        for option in recommendation.ranked_options
    )


def has_audit_trail(recommendation: Recommendation) -> bool:
    """Phase 11 Evaluation Metrics table: "Auditability"."""
    return bool(recommendation.audit_id)


def recommendation_quality_percent(recommendations: list[Recommendation]) -> float:
    return percent_matching(recommendations, has_complete_option_fields)


def auditability_percent(recommendations: list[Recommendation]) -> float:
    return percent_matching(recommendations, has_audit_trail)
