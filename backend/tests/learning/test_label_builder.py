from datetime import date

from learning.label_builder import build_label
from models.core_schema import CommodityType
from models.learning_schema import HistoricalCase, ObservedOutcome


def _case(**outcome_overrides) -> HistoricalCase:
    outcome_defaults = dict(
        average_delay_days=12.0, freight_cost_increase_percent=20.0, route_shift_detected=True, price_movement_percent=5.0
    )
    outcome_defaults.update(outcome_overrides)
    return HistoricalCase(
        case_id="CASE-1",
        case_name="Test case",
        commodity_type=CommodityType.CRUDE_OIL,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 2, 15),
        trigger_events=["MARITIME_ATTACK"],
        affected_corridors=["RED_SEA"],
        observed_outcomes=ObservedOutcome(**outcome_defaults),
        is_simulated=True,
    )


def test_material_case_is_labelled_disruptive():
    label = build_label(_case())
    assert label.materially_disruptive is True
    assert label.delay_band == "LONG"
    assert label.reroute_occurred is True


def test_minor_case_is_not_labelled_disruptive():
    label = build_label(
        _case(average_delay_days=1.0, freight_cost_increase_percent=2.0, price_movement_percent=1.0, route_shift_detected=False)
    )
    assert label.materially_disruptive is False
    assert label.delay_band == "SHORT"
    assert label.price_impact_band == "LOW"
