"""Generates the executive crisis-response report from event, risk, scenario, and recommendation context (Phase 8, section 8.3)."""

from __future__ import annotations

from datetime import datetime

from models.recommendation_schema import Recommendation
from models.scenario_schema import ScenarioResult


def build_markdown_report(
    *, report_id: str, generated_at: datetime, scenario: ScenarioResult, recommendation: Recommendation
) -> str:
    """Renders a human-readable Markdown crisis-response brief (section 8.3
    output: "Markdown or PDF-ready report payload")."""
    lines = [
        f"# EnergyShield Executive Brief - {scenario.scenario_type}",
        "",
        f"**Report ID:** {report_id}  ",
        f"**Generated:** {generated_at.isoformat()}  ",
        f"**Scenario:** {scenario.scenario_id}  |  **Recommendation:** {recommendation.recommendation_id}"
        f"  |  **Audit:** {recommendation.audit_id}",
        "",
        "## Executive Summary",
        (
            f"{scenario.commodity_type} disruption scenario `{scenario.scenario_type}` places "
            f"**{scenario.supply_at_risk_percent}%** of supply at risk with an estimated "
            f"**{scenario.estimated_delay_days}-day** delay and a **{scenario.freight_cost_impact_percent}%** "
            "freight cost impact."
        ),
        "",
        "## Affected Refineries",
    ]

    if scenario.affected_refineries:
        for refinery in scenario.affected_refineries:
            lines.append(f"- **{refinery.refinery_id}** ({refinery.exposure_level}): {refinery.reason}")
    else:
        lines.append("- No specific refinery exposure resolved.")

    lines += ["", "## Recommended Actions"]
    if recommendation.ranked_options:
        for option in recommendation.ranked_options:
            lines.append(
                f"{option.rank}. **{option.supplier}** via {option.route} - {option.action_priority} "
                f"(feasibility {option.feasibility_score}, delay {option.estimated_delay_days}d, "
                f"cost impact {option.cost_impact_percent}%)"
            )
    else:
        lines.append("- No alternative procurement options resolved for this scenario.")

    if recommendation.spr_plan is not None:
        lines += ["", "## Strategic Reserve Action"]
        if recommendation.spr_plan.drawdown_required:
            lines.append(
                f"Drawdown recommended: {recommendation.spr_plan.drawdown_percent}% starting day "
                f"{recommendation.spr_plan.start_day}. {recommendation.spr_plan.reason}"
            )
        else:
            lines.append(f"No drawdown required. {recommendation.spr_plan.reason}")

    lines += ["", "## Assumptions"]
    for assumption in scenario.assumptions + recommendation.assumptions:
        marker = "(simulated)" if assumption.is_simulated else "(observed)"
        lines.append(f"- {assumption.description} {marker}")

    lines += ["", f"**Confidence:** scenario {scenario.confidence}, recommendation {recommendation.confidence}"]
    return "\n".join(lines)
