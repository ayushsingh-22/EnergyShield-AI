"""Converts historical disruption outcomes into training/calibration labels (Phase 13, section 13.3)."""

from __future__ import annotations

from dataclasses import dataclass

from models.learning_schema import HistoricalCase, ObservedOutcome

# Delay/price bands are deliberately coarse (section 13.3: "label observed
# delay band" / "label observed price impact band") rather than raw
# numbers, since backtesting and calibration compare *bands* against
# predicted risk levels, not exact regression targets. Each tuple is
# (upper bound inclusive, band label); the last band catches everything
# above the previous thresholds.
_DELAY_BANDS: list[tuple[float, str]] = [(3, "SHORT"), (10, "MEDIUM"), (float("inf"), "LONG")]
_PRICE_BANDS: list[tuple[float, str]] = [(3, "LOW"), (8, "MEDIUM"), (float("inf"), "HIGH")]

# A case counts as "materially disruptive" (section 13.3, step 1) if any
# observed outcome crosses these floors - mirrors the same order of
# magnitude `scenarios/scenario_engine.py` uses for
# `recommended_action_required`.
_MATERIAL_DELAY_DAYS = 5.0
_MATERIAL_FREIGHT_COST_PERCENT = 10.0
_MATERIAL_PRICE_MOVEMENT_PERCENT = 5.0


def _band(value: float | None, thresholds: list[tuple[float, str]]) -> str | None:
    if value is None:
        return None
    for threshold, label in thresholds:
        if value <= threshold:
            return label
    return thresholds[-1][1]


@dataclass
class CaseLabel:
    case_id: str
    materially_disruptive: bool
    delay_band: str | None
    price_impact_band: str | None
    reroute_occurred: bool | None


def build_label(case: HistoricalCase) -> CaseLabel:
    outcome: ObservedOutcome = case.observed_outcomes
    materially_disruptive = bool(
        (outcome.average_delay_days or 0) >= _MATERIAL_DELAY_DAYS
        or (outcome.freight_cost_increase_percent or 0) >= _MATERIAL_FREIGHT_COST_PERCENT
        or (outcome.price_movement_percent or 0) >= _MATERIAL_PRICE_MOVEMENT_PERCENT
    )
    return CaseLabel(
        case_id=case.case_id,
        materially_disruptive=materially_disruptive,
        delay_band=_band(outcome.average_delay_days, _DELAY_BANDS),
        price_impact_band=_band(outcome.price_movement_percent, _PRICE_BANDS),
        reroute_occurred=outcome.route_shift_detected,
    )


def build_labels(cases: list[HistoricalCase]) -> list[CaseLabel]:
    return [build_label(case) for case in cases]
