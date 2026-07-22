"""Central registry of source URLs, refresh intervals, reliability tiers, and fallback modes (Phase 1, section 1.1)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional
from models.data_source_schema import DataSourceDefinition
from models.core_schema import SourceReliability


_REGISTRY: Dict[str, DataSourceDefinition] = {
    "gdelt": DataSourceDefinition(
        source_name="gdelt",
        category="news",
        url="https://api.gdeltproject.org/api/v2/doc/doc?query=energy",
        refresh_interval_minutes=15,
        reliability_tier=SourceReliability.MEDIUM,
        fallback_mode="seeded_sample",
        enabled=True,
    ),
    "maritime_alerts": DataSourceDefinition(
        source_name="maritime_alerts",
        category="maritime",
        url="https://api.maritime-alerts.example.com",
        refresh_interval_minutes=30,
        reliability_tier=SourceReliability.HIGH,
        fallback_mode="seeded_sample",
        enabled=True,
    ),
    "sanctions": DataSourceDefinition(
        source_name="sanctions",
        category="sanctions",
        url="https://ofac.treasury.gov/api",
        refresh_interval_minutes=1440, # Daily
        reliability_tier=SourceReliability.OFFICIAL,
        fallback_mode="seeded_sample",
        enabled=True,
    ),
    "commodity_prices": DataSourceDefinition(
        source_name="commodity_prices",
        category="prices",
        url="https://api.eia.gov/v2/seriesid",
        refresh_interval_minutes=1440, # Daily
        reliability_tier=SourceReliability.HIGH,
        fallback_mode="seeded_sample",
        enabled=True,
    ),
    "lng_prices": DataSourceDefinition(
        source_name="lng_prices",
        category="prices",
        url="https://api.eia.gov/v2/natural-gas/pri/fut/data/",
        refresh_interval_minutes=1440, # Daily
        reliability_tier=SourceReliability.HIGH,
        fallback_mode="seeded_sample",
        enabled=True,
    ),
    "coal_prices": DataSourceDefinition(
        source_name="coal_prices",
        category="prices",
        url="https://www.worldbank.org/en/research/commodity-markets",
        refresh_interval_minutes=43200, # Monthly (Pink Sheet cadence)
        reliability_tier=SourceReliability.HIGH,
        fallback_mode="seeded_sample",
        enabled=True,
    ),
    "ais_stream": DataSourceDefinition(
        source_name="ais_stream",
        category="vessel_movement",
        url="wss://stream.aisstream.io/v0/stream",
        refresh_interval_minutes=1, # Real-time/demo
        reliability_tier=SourceReliability.LOW,
        fallback_mode="seeded_sample",
        enabled=True,
    ),
    "portwatch": DataSourceDefinition(
        source_name="portwatch",
        category="chokepoint_activity",
        url="https://portwatch.imf.org/api",
        refresh_interval_minutes=10080, # Weekly
        reliability_tier=SourceReliability.HIGH,
        fallback_mode="seeded_sample",
        enabled=True,
    ),
    "import_baseline": DataSourceDefinition(
        source_name="import_baseline",
        category="baseline",
        url="https://ppac.gov.in/api",
        refresh_interval_minutes=43200, # Monthly
        reliability_tier=SourceReliability.SIMULATED,
        fallback_mode="seeded_sample",
        enabled=True,
    ),
}

def get_active_sources() -> List[DataSourceDefinition]:
    """Returns a list of all enabled data sources."""
    return [source for source in _REGISTRY.values() if source.enabled]

def get_source(source_name: str) -> Optional[DataSourceDefinition]:
    """Returns a specific data source definition by name."""
    return _REGISTRY.get(source_name)

def get_source_reliability(source_name: str) -> SourceReliability:
    """Returns the reliability tier of a specific source."""
    source = _REGISTRY.get(source_name)
    if source:
        return source.reliability_tier
    return SourceReliability.LOW  # Default fallback


# Real fetch-attempt history, keyed by source_name, so `/api/v1/data/freshness`
# reports actual state instead of fabricating "now"/"healthy" on every call.
# Populated by `record_fetch_attempt` whenever a collector's `.fetch()` is
# actually invoked (see `api/routes/data_sources.py` and `api/routes/events.py`).
_FRESHNESS_STATE: Dict[str, Dict[str, object]] = {}


def record_fetch_attempt(source_name: str, success: bool) -> None:
    """Records the outcome of one real collector fetch attempt for `source_name`."""
    now = datetime.now(timezone.utc)
    state = _FRESHNESS_STATE.setdefault(
        source_name,
        {"last_successful_fetch_at": None, "last_attempt_at": None, "consecutive_failures": 0},
    )
    state["last_attempt_at"] = now
    if success:
        state["last_successful_fetch_at"] = now
        state["consecutive_failures"] = 0
    else:
        state["consecutive_failures"] = int(state["consecutive_failures"]) + 1


def get_freshness_state(source_name: str) -> Dict[str, object]:
    """Returns the recorded fetch state for `source_name`, or the
    "never attempted" default if no collector has run yet for it."""
    return _FRESHNESS_STATE.get(
        source_name,
        {"last_successful_fetch_at": None, "last_attempt_at": None, "consecutive_failures": 0},
    )
