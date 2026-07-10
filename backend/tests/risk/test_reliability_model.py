from datetime import datetime, timezone

from models.core_schema import CommodityType, RiskEventType, SourceReliability
from models.event_schema import RiskEvent
from risk import reliability_model


def _event(source_name, reliability, event_id="EVT-1"):
    return RiskEvent(
        event_id=event_id,
        event_type=RiskEventType.MARITIME_ATTACK,
        commodity_type=CommodityType.CRUDE_OIL,
        title="t",
        summary="s",
        detected_at=datetime.now(timezone.utc),
        source_name=source_name,
        source_reliability=reliability,
        severity=3,
        confidence=0.7,
    )


def test_compute_source_reliability_score_empty_is_zero():
    assert reliability_model.compute_source_reliability_score([]) == 0.0


def test_compute_source_reliability_score_official_higher_than_low():
    official_score = reliability_model.compute_source_reliability_score(
        [_event("sanctions", SourceReliability.OFFICIAL)]
    )
    low_score = reliability_model.compute_source_reliability_score([_event("ais_stream", SourceReliability.LOW)])

    assert official_score > low_score


def test_compute_corroboration_bonus_zero_for_single_source():
    events = [_event("gdelt", SourceReliability.MEDIUM, "EVT-1"), _event("gdelt", SourceReliability.MEDIUM, "EVT-2")]
    assert reliability_model.compute_corroboration_bonus(events) == 0.0


def test_compute_corroboration_bonus_positive_for_multiple_sources():
    events = [
        _event("gdelt", SourceReliability.MEDIUM, "EVT-1"),
        _event("ais_stream", SourceReliability.MEDIUM, "EVT-2"),
    ]
    assert reliability_model.compute_corroboration_bonus(events) > 0.0


def test_compute_corroboration_bonus_capped_at_fifteen():
    events = [_event(f"source-{i}", SourceReliability.MEDIUM, f"EVT-{i}") for i in range(10)]
    assert reliability_model.compute_corroboration_bonus(events) == 15.0
