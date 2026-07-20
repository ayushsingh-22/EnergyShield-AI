"""Calculates supply gap, shipping delay, freight cost impact, and refinery exposure for a scenario run (Phase 6, section 6.2).

Kept separate from `scenario_engine.py` so the pure impact math (severity/
duration scaling, manual-override application, confidence discounting) is
independently testable from template loading and graph/digital-twin
resolution.
"""

from __future__ import annotations

from typing import Sequence

from models.core_schema import RiskLevel

# Where each severity level sits along a template's [low, high] impact
# range. CRITICAL saturates at the top of the range; LOW sits near the
# bottom rather than at zero, since even a "low" severity disruption still
# has some measurable impact per the scenario's own assumptions.
_SEVERITY_POSITION: dict[RiskLevel, float] = {
    RiskLevel.LOW: 0.15,
    RiskLevel.MEDIUM: 0.40,
    RiskLevel.HIGH: 0.65,
    RiskLevel.SEVERE: 0.85,
    RiskLevel.CRITICAL: 1.0,
}


def _severity_scaled(value_range: tuple[float, float], severity: RiskLevel) -> float:
    low, high = value_range
    position = _SEVERITY_POSITION[severity]
    return low + (high - low) * position


def compute_supply_at_risk_percent(
    supply_reduction_percent_range: tuple[float, float],
    severity: RiskLevel,
    manual_overrides: dict[str, float],
    overrides_used: list[str],
) -> float:
    override = manual_overrides.get("supply_reduction_percent")
    if override is not None:
        overrides_used.append("supply_reduction_percent")
        return round(max(0.0, min(100.0, override)), 1)
    return round(_severity_scaled(supply_reduction_percent_range, severity), 1)


_MAX_FREIGHT_COST_IMPACT_PERCENT = 300.0


def compute_freight_cost_impact_percent(
    freight_cost_increase_percent_range: tuple[float, float],
    severity: RiskLevel,
    manual_overrides: dict[str, float],
    overrides_used: list[str],
) -> float:
    override = manual_overrides.get("freight_cost_increase_percent")
    if override is not None:
        overrides_used.append("freight_cost_increase_percent")
        return round(max(0.0, min(_MAX_FREIGHT_COST_IMPACT_PERCENT, override)), 1)
    return round(_severity_scaled(freight_cost_increase_percent_range, severity), 1)


def compute_estimated_delay_days(
    *,
    default_duration_days: int,
    duration_days: int,
    severity: RiskLevel,
    affected_route_transit_days: Sequence[float],
    manual_overrides: dict[str, float],
    overrides_used: list[str],
) -> float:
    """Route-specific transit time is the preferred basis (plan section
    6.2, step 3: "estimate shipping delay using route-specific
    assumptions"); when no route resolves, falls back to a fraction of the
    template's default duration. Either way the result is capped at the
    request's own `duration_days` - a scenario cannot claim a delay longer
    than the disruption itself is modelled to last."""
    override = manual_overrides.get("estimated_delay_days")
    if override is not None:
        overrides_used.append("estimated_delay_days")
        return round(max(0.0, override), 1)

    position = _SEVERITY_POSITION[severity]
    if affected_route_transit_days:
        base = sum(affected_route_transit_days) / len(affected_route_transit_days)
        delay = base * (0.3 + position * 0.9)
    else:
        delay = default_duration_days * (0.2 + position * 0.4)
    return round(min(delay, float(duration_days)), 1)


def compute_confidence(
    *,
    manual_overrides_used: list[str],
    resolved_specific_entities: bool,
    duration_days: int,
    default_duration_days: int,
    stale_baseline: bool,
) -> float:
    """Confidence discounting rules per docs/SCENARIO_ASSUMPTIONS.md: reduce
    when manual overrides replace graph/exposure-derived defaults, when
    affected entities couldn't be matched to specific digital-twin nodes,
    when the requested duration extrapolates far from the template's
    analyst-set default, or when the India import baseline is stale."""
    confidence = 0.86
    if manual_overrides_used:
        confidence -= 0.12
    if not resolved_specific_entities:
        confidence -= 0.15
    if default_duration_days and abs(duration_days - default_duration_days) / default_duration_days > 0.5:
        confidence -= 0.05
    if stale_baseline:
        confidence -= 0.06
    return round(max(0.4, min(0.95, confidence)), 2)
