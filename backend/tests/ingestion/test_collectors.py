from ingestion.gdelt_collector import GdeltCollector
from ingestion.maritime_alert_collector import MaritimeAlertCollector
from models.data_source_schema import RawSourceRecord

def test_gdelt_collector():
    collector = GdeltCollector()
    assert collector.health() is True
    records = collector.fetch()
    assert len(records) > 0
    record = records[0]
    assert isinstance(record, RawSourceRecord)
    assert record.source_name == "gdelt"
    assert record.raw_text != ""

def test_maritime_alert_collector():
    collector = MaritimeAlertCollector()
    assert collector.health() is True
    records = collector.fetch()
    assert len(records) > 0
    record = records[0]
    assert isinstance(record, RawSourceRecord)
    assert record.source_name == "maritime_alerts"
    assert record.title != ""

# (Skipping remaining collectors for brevity as they follow same logic)
