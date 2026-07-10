from datetime import datetime, timezone

from ml import event_classifier
from models.core_schema import RiskEventType, SourceReliability
from models.data_source_schema import NormalizedSignal


def _signal(title, raw_text, source_name="gdelt", reliability=SourceReliability.MEDIUM):
    return NormalizedSignal(
        signal_id="sig-1",
        source=source_name,
        source_name=source_name,
        source_reliability=reliability,
        reliability=reliability,
        detected_at=datetime.now(timezone.utc),
        title=title,
        raw_text=raw_text,
    )


def test_classify_event_type_maritime_attack():
    signal = _signal("Tanker attacked near Hormuz", "An oil tanker was attacked in the Strait of Hormuz.")
    assert event_classifier.classify_event_type(signal) == RiskEventType.MARITIME_ATTACK


def test_classify_event_type_sanction_keyword_overrides_source():
    signal = _signal("Sanctions expanded", "New sanctions imposed on shipping firms.", source_name="gdelt")
    assert event_classifier.classify_event_type(signal) == RiskEventType.SANCTION_UPDATE


def test_classify_event_type_falls_back_to_source_default():
    signal = _signal("Update", "Routine daily update with no notable keywords.", source_name="commodity_prices")
    assert event_classifier.classify_event_type(signal) == RiskEventType.PRICE_SPIKE


def test_classify_event_type_unknown_source_and_text_returns_none():
    signal = _signal(None, "Nothing notable here.", source_name="unknown_source")
    assert event_classifier.classify_event_type(signal) is None


def test_estimate_severity_base_and_intensity_adjustment():
    base = event_classifier.estimate_severity(RiskEventType.MARITIME_ATTACK, "an incident occurred")
    upgraded = event_classifier.estimate_severity(RiskEventType.MARITIME_ATTACK, "a major explosion occurred")
    downgraded = event_classifier.estimate_severity(RiskEventType.MARITIME_ATTACK, "a minor incident occurred")
    assert upgraded > base > downgraded


def test_estimate_severity_clamped_to_valid_range():
    severity = event_classifier.estimate_severity(RiskEventType.WEATHER_DISRUPTION, "a minor storm")
    assert 1 <= severity <= 5


def test_get_scenario_triggers_from_chokepoint():
    triggers = event_classifier.get_scenario_triggers(RiskEventType.MARITIME_ATTACK, ["CHK_HORMUZ"])
    assert triggers == ["HORMUZ_PARTIAL_CLOSURE"]


def test_get_scenario_triggers_from_event_type():
    triggers = event_classifier.get_scenario_triggers(RiskEventType.SANCTION_UPDATE, [])
    assert triggers == ["SANCTIONS_SHOCK"]


def test_get_scenario_triggers_combines_and_dedupes():
    triggers = event_classifier.get_scenario_triggers(RiskEventType.CHOKEPOINT_CONGESTION, ["CHK_BAB", "CHK_SUEZ"])
    assert triggers == ["PORT_CONGESTION", "RED_SEA_SHIPPING_DISRUPTION"]
