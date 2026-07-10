"""Data freshness and source health endpoints (Phase 1 ingestion foundation).

See docs/API_REFERENCE.md for the endpoints this router will own.
"""

from __future__ import annotations

import logging
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter

from models.data_source_schema import DataSourceDefinition, SourceFreshness
from ingestion.source_registry import get_active_sources, get_freshness_state, record_fetch_attempt
from ingestion.ais_collector import AisCollector
from ingestion.commodity_price_collector import CommodityPriceCollector
from ingestion.gdelt_collector import GdeltCollector
from ingestion.import_baseline_collector import ImportBaselineCollector
from ingestion.maritime_alert_collector import MaritimeAlertCollector
from ingestion.portwatch_collector import PortwatchCollector
from ingestion.sanctions_collector import SanctionsCollector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/data", tags=["data-sources"])

# One real fetch per registered collector at import time, so `/freshness`
# reports genuine last-fetch state instead of fabricating "now"/"healthy"
# on every request. `api/routes/events.py` records further real attempts
# whenever its extraction pipeline re-fetches this same subset of sources.
_BOOTSTRAP_COLLECTORS = [
    GdeltCollector(),
    MaritimeAlertCollector(),
    SanctionsCollector(),
    CommodityPriceCollector(),
    AisCollector(),
    PortwatchCollector(),
    ImportBaselineCollector(),
]


def _bootstrap_freshness_state() -> None:
    for collector in _BOOTSTRAP_COLLECTORS:
        try:
            collector.fetch()
            record_fetch_attempt(collector.source_name, success=True)
        except Exception:  # noqa: BLE001 - one bad source must not block the others
            logger.exception("Bootstrap fetch failed for source %s", collector.source_name)
            record_fetch_attempt(collector.source_name, success=False)


try:
    _bootstrap_freshness_state()
except Exception:  # noqa: BLE001 - startup bootstrap must never crash the app
    logger.exception("Data source freshness bootstrap failed")


@router.get("/freshness", response_model=List[SourceFreshness])
def get_data_freshness():
    """Returns the freshness status of all active data sources, from real
    recorded fetch attempts rather than the current wall-clock time."""
    sources = get_active_sources()
    freshness_list = []

    for source in sources:
        state = get_freshness_state(source.source_name)
        consecutive_failures = int(state["consecutive_failures"])
        freshness_list.append(
            SourceFreshness(
                source_name=source.source_name,
                last_successful_fetch_at=state["last_successful_fetch_at"],
                last_attempt_at=state["last_attempt_at"],
                is_healthy=state["last_attempt_at"] is not None and consecutive_failures == 0,
                consecutive_failures=consecutive_failures,
                reliability_tier=source.reliability_tier,
            )
        )
    return freshness_list


@router.get("/sources", response_model=List[DataSourceDefinition])
def get_data_sources():
    """Returns the list of all registered data sources."""
    return get_active_sources()


@router.get("/health")
def get_data_health():
    """Returns the overall health of the ingestion pipeline."""
    sources = get_active_sources()
    total_sources = len(sources)
    unhealthy_sources = [
        source.source_name
        for source in sources
        if int(get_freshness_state(source.source_name)["consecutive_failures"]) > 0
    ]
    return {
        "status": "healthy" if total_sources > 0 and not unhealthy_sources else "degraded",
        "active_sources": total_sources,
        "unhealthy_sources": unhealthy_sources,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
