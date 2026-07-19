"""Suggests strategic petroleum reserve drawdown schedules based on supply gap and scenario duration (Phase 7, section 7.3)."""

from __future__ import annotations

from models.core_schema import RiskLevel
from models.recommendation_schema import SprPlan
from services.digital_twin_service import DigitalTwinService

_EMERGENCY_SEVERITY_LEVELS = {RiskLevel.SEVERE, RiskLevel.CRITICAL}
_MIN_SUPPLY_AT_RISK_PERCENT = 10.0
_MIN_DELAY_DAYS = 5.0
_EMERGENCY_MIN_DURATION_DAYS = 30


def recommend_spr_plan(
    *,
    supply_at_risk_percent: float,
    estimated_delay_days: float,
    duration_days: int,
    severity: RiskLevel,
    digital_twin: DigitalTwinService | None = None,
) -> SprPlan:
    """Section 7.3 rules: avoid drawdown for short, low-severity shocks;
    recommend a controlled drawdown once the supply gap persists past
    normal operating buffers; reserve an emergency-sized drawdown for
    high/critical-severity, extended-duration scenarios."""
    if supply_at_risk_percent < _MIN_SUPPLY_AT_RISK_PERCENT or estimated_delay_days < _MIN_DELAY_DAYS:
        return SprPlan(
            drawdown_required=False,
            reason=(
                f"Supply at risk ({supply_at_risk_percent}%) and delay ({estimated_delay_days}d) stay "
                "within normal operating buffers; SPR drawdown is not warranted."
            ),
        )

    emergency = severity in _EMERGENCY_SEVERITY_LEVELS and duration_days >= _EMERGENCY_MIN_DURATION_DAYS
    drawdown_percent = round(min(30.0, supply_at_risk_percent * (0.6 if emergency else 0.35)), 1)
    start_day = 1 if emergency else max(1, min(7, int(estimated_delay_days // 2)))

    capacity_note = ""
    if digital_twin is not None:
        total_capacity_mmbbl = sum(site.capacity_mmbbl or 0 for site in digital_twin.get_spr_sites())
        if total_capacity_mmbbl > 0:
            capacity_note = f" Against {total_capacity_mmbbl:.1f} MMbbl of total seeded reserve capacity."

    reason = (
        "Severe/critical, extended-duration disruption: emergency drawdown starts immediately."
        if emergency
        else "Supply gap persists beyond short-term buffers: controlled drawdown once early delay is confirmed."
    ) + capacity_note

    return SprPlan(
        drawdown_required=True,
        start_day=start_day,
        drawdown_percent=drawdown_percent,
        reason=reason,
    )
