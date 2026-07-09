"""Data freshness and source health endpoints (Phase 1 ingestion foundation).

See docs/API_REFERENCE.md for the endpoints this router will own.
"""

from __future__ import annotations

from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter

from models.data_source_schema import DataSourceDefinition, SourceFreshness
from ingestion.source_registry import get_active_sources

router = APIRouter(prefix="/api/v1/data", tags=["data-sources"])

@router.get("/freshness", response_model=List[SourceFreshness])
def get_data_freshness():
    """Returns the freshness status of all active data sources."""
    sources = get_active_sources()
    freshness_list = []
    
    # Mock data for Phase 1 MVP
    now = datetime.now(timezone.utc)
    for source in sources:
        freshness_list.append(SourceFreshness(
            source_name=source.source_name,
            last_successful_fetch_at=now,
            last_attempt_at=now,
            is_healthy=True,
            consecutive_failures=0,
            reliability_tier=source.reliability_tier
        ))
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
    # Simple check for demo purposes
    healthy = total_sources > 0
    return {
        "status": "healthy" if healthy else "unhealthy",
        "active_sources": total_sources,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
