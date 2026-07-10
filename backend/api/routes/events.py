"""Latest event feed and event detail endpoints (Phase 4 geopolitical event
extraction agent).

Runs the Phase 1 ingestion collectors through the normalizer and the
Phase 4 extraction agent once at import time - the same
"load-once-at-module-import" pattern `api/routes/digital_twin.py` uses for
seed data - and pushes every extracted event into the knowledge graph via
`relationship_builder.upsert_event_relationships`, the integration point
Phase 3 built for exactly this purpose.

See docs/API_REFERENCE.md for the endpoints this router owns.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query

from agents.event_extraction_agent import EventExtractionAgent
from graph.relationship_builder import upsert_event_relationships
from ingestion.ais_collector import AisCollector
from ingestion.commodity_price_collector import CommodityPriceCollector
from ingestion.data_normalizer import DataNormalizer
from ingestion.gdelt_collector import GdeltCollector
from ingestion.maritime_alert_collector import MaritimeAlertCollector
from ingestion.portwatch_collector import PortwatchCollector
from ingestion.sanctions_collector import SanctionsCollector
from ingestion.source_registry import record_fetch_attempt
from models.event_schema import RiskEvent
from services.event_service import EventService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/events", tags=["events"])

_collectors = [
    GdeltCollector(),
    MaritimeAlertCollector(),
    SanctionsCollector(),
    CommodityPriceCollector(),
    AisCollector(),
    PortwatchCollector(),
]
_normalizer = DataNormalizer()
_extraction_agent = EventExtractionAgent()
_event_service = EventService()


def run_extraction_pipeline() -> list[RiskEvent]:
    """Fetches every collector, normalizes, extracts structured events, and
    links each one into the knowledge graph. Never raises - a broken
    collector or an unreachable graph must not take down the events feed.

    Treats each run as a full refresh of current state rather than an
    incremental append: the event-id sequence resets and the event store is
    replaced wholesale, so calling this more than once (e.g. from a future
    Phase 10 scheduler) can't accumulate unbounded duplicate events for
    content the seeded collectors return on every call.
    """
    raw_records = []
    for collector in _collectors:
        try:
            raw_records.extend(collector.fetch())
            record_fetch_attempt(collector.source_name, success=True)
        except Exception:  # noqa: BLE001 - one bad collector must not break ingestion
            logger.exception("Collector %s failed during events pipeline run", collector.source_name)
            record_fetch_attempt(collector.source_name, success=False)

    signals = _normalizer.normalize(raw_records)
    _extraction_agent.reset_event_sequence()
    results = _extraction_agent.extract_batch(signals)

    events: list[RiskEvent] = []
    for result in results:
        if not result.succeeded or result.event is None:
            logger.info("Signal %s not converted to an event: %s", result.signal_id, result.error_message)
            continue
        events.append(result.event)
        try:
            upsert_event_relationships(result.event)
        except Exception:  # noqa: BLE001 - graph write failures must not drop the event
            logger.exception("Failed to link event %s into knowledge graph", result.event.event_id)

    return _event_service.replace_all(events)


try:
    run_extraction_pipeline()
except Exception:  # noqa: BLE001 - startup bootstrap must never crash the app
    logger.exception("Initial events pipeline run failed")


@router.get("/latest", response_model=list[RiskEvent])
def get_latest_events(limit: int = Query(default=50, ge=1, le=200)):
    """Most recently detected structured risk events."""
    return _event_service.get_latest(limit)


@router.get("/{event_id}", response_model=RiskEvent)
def get_event(event_id: str):
    """Single event detail."""
    event = _event_service.get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
    return event


def get_event_service() -> EventService:
    """Exposes the module-level `EventService` singleton to other routers
    (Phase 5's `api/routes/risk.py` reads the current event set from here
    rather than re-running the ingestion pipeline itself)."""
    return _event_service
