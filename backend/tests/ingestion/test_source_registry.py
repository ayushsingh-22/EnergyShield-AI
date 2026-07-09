from ingestion.source_registry import get_active_sources, get_source, get_source_reliability
from models.core_schema import SourceReliability

def test_get_active_sources():
    sources = get_active_sources()
    assert len(sources) > 0
    # Check that gdelt is present
    assert any(s.source_name == "gdelt" for s in sources)

def test_get_source():
    source = get_source("gdelt")
    assert source is not None
    assert source.source_name == "gdelt"

def test_get_source_not_found():
    source = get_source("non_existent")
    assert source is None

def test_get_source_reliability():
    reliability = get_source_reliability("gdelt")
    assert reliability == SourceReliability.MEDIUM

def test_get_source_reliability_default():
    reliability = get_source_reliability("unknown_source")
    assert reliability == SourceReliability.LOW
