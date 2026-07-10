from datetime import datetime, timezone

from models.core_schema import CommodityType, RiskEventType, SourceReliability
from models.event_schema import RiskEvent
from risk import anomaly_model


def _event(event_type, severity):
    return RiskEvent(
        event_id="EVT-1",
        event_type=event_type,
        commodity_type=CommodityType.CRUDE_OIL,
        title="t",
        summary="s",
        detected_at=datetime.now(timezone.utc),
        source_name="test",
        source_reliability=SourceReliability.MEDIUM,
        severity=severity,
        confidence=0.7,
    )


def test_compute_ais_anomaly_score_zero_without_matching_events():
    assert anomaly_model.compute_ais_anomaly_score([_event(RiskEventType.SANCTION_UPDATE, 5)]) == 0.0


def test_compute_ais_anomaly_score_scales_with_severity():
    assert anomaly_model.compute_ais_anomaly_score([_event(RiskEventType.AIS_REROUTING, 3)]) == 60.0


def test_compute_ais_anomaly_score_includes_congestion():
    assert anomaly_model.compute_ais_anomaly_score([_event(RiskEventType.CHOKEPOINT_CONGESTION, 4)]) == 80.0


def test_compute_price_movement_score_zero_without_price_spike():
    assert anomaly_model.compute_price_movement_score([_event(RiskEventType.MARITIME_ATTACK, 5)]) == 0.0


def test_compute_price_movement_score_scales_with_severity():
    assert anomaly_model.compute_price_movement_score([_event(RiskEventType.PRICE_SPIKE, 5)]) == 100.0


def test_compute_sanctions_score_zero_without_sanction_event():
    assert anomaly_model.compute_sanctions_score([_event(RiskEventType.MARITIME_ATTACK, 5)]) == 0.0


def test_compute_sanctions_score_scales_with_severity():
    assert anomaly_model.compute_sanctions_score([_event(RiskEventType.SANCTION_UPDATE, 4)]) == 80.0
