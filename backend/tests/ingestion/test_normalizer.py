from datetime import datetime, timezone
from ingestion.data_normalizer import DataNormalizer
from models.data_source_schema import RawSourceRecord
from models.core_schema import CommodityType, SourceReliability

def test_data_normalizer():
    normalizer = DataNormalizer()
    now = datetime.now(timezone.utc)
    
    raw = RawSourceRecord(
        source_name="test_source",
        reliability_tier=SourceReliability.MEDIUM,
        detected_at=now,
        title="Test Event",
        raw_text="This is a test event.",
        url="https://example.com/test1"
    )
    
    signals = normalizer.normalize([raw])
    assert len(signals) == 1
    
    signal = signals[0]
    assert signal.title == "Test Event"
    assert signal.source_name == "test_source"
    assert signal.event_candidate is True

def test_data_normalizer_deduplication():
    normalizer = DataNormalizer()
    now = datetime.now(timezone.utc)
    
    raw1 = RawSourceRecord(
        source_name="test_source",
        reliability_tier=SourceReliability.MEDIUM,
        detected_at=now,
        title="Duplicate Event",
        raw_text="This is a duplicate event.",
        url="https://example.com/duplicate"
    )
    
    raw2 = RawSourceRecord(
        source_name="test_source",
        reliability_tier=SourceReliability.MEDIUM,
        detected_at=now,
        title="Duplicate Event",  # Same title
        raw_text="This is a duplicate event.", # Same text
        url="https://example.com/duplicate" # Same url
    )
    
    signals = normalizer.normalize([raw1, raw2])
    assert len(signals) == 1  # The second one should be filtered out


def test_data_normalizer_defaults_commodity_type_to_crude_oil():
    normalizer = DataNormalizer()
    raw = RawSourceRecord(
        source_name="gdelt",
        reliability_tier=SourceReliability.MEDIUM,
        detected_at=datetime.now(timezone.utc),
        title="Some headline",
        raw_text="Some body text with no chokepoint mention.",
    )

    signal = normalizer.normalize([raw])[0]

    assert signal.commodity_type == CommodityType.CRUDE_OIL


def test_data_normalizer_detects_corridor_hint_from_location_name():
    normalizer = DataNormalizer()
    raw = RawSourceRecord(
        source_name="maritime_alerts",
        reliability_tier=SourceReliability.HIGH,
        detected_at=datetime.now(timezone.utc),
        title="Advisory",
        raw_text="Suspicious approach reported.",
        location_name="Strait of Hormuz",
    )

    signal = normalizer.normalize([raw])[0]

    assert signal.corridor_hint == "CHK_HORMUZ"


def test_data_normalizer_corridor_hint_is_none_when_unresolvable():
    normalizer = DataNormalizer()
    raw = RawSourceRecord(
        source_name="gdelt",
        reliability_tier=SourceReliability.MEDIUM,
        detected_at=datetime.now(timezone.utc),
        title="Generic headline",
        raw_text="Nothing corridor-specific here.",
    )

    signal = normalizer.normalize([raw])[0]

    assert signal.corridor_hint is None


def test_data_normalizer_corridor_hint_does_not_false_positive_on_substring():
    normalizer = DataNormalizer()
    raw = RawSourceRecord(
        source_name="gdelt",
        reliability_tier=SourceReliability.MEDIUM,
        detected_at=datetime.now(timezone.utc),
        title="Unrelated headline",
        raw_text="This mentions issues and values but no real corridor.",
    )

    signal = normalizer.normalize([raw])[0]

    assert signal.corridor_hint is None
