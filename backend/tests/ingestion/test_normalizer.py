from datetime import datetime, timezone
from ingestion.data_normalizer import DataNormalizer
from models.data_source_schema import RawSourceRecord
from models.core_schema import SourceReliability

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
