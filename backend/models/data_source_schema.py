"""Schemas for data sources, raw records, and normalized signals (Phase 1)."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from models.core_schema import (
    CommodityType,
    Coordinates,
    EnergyShieldBaseModel,
    SourceReliability,
)


class DataSourceDefinition(EnergyShieldBaseModel):
    """One entry in the source registry (backend/ingestion/source_registry.py)."""

    source_name: str
    category: str
    url: str | None = None
    refresh_interval_minutes: int = Field(..., gt=0)
    reliability_tier: SourceReliability
    fallback_mode: str = Field(
        default="seeded_sample",
        description="What the collector does when the live source is unreachable.",
    )
    enabled: bool = True


class SourceFreshness(EnergyShieldBaseModel):
    """Backs GET /api/v1/data/freshness."""

    source_name: str
    last_successful_fetch_at: datetime | None = None
    last_attempt_at: datetime | None = None
    is_healthy: bool
    consecutive_failures: int = 0
    reliability_tier: SourceReliability


class RawSourceRecord(EnergyShieldBaseModel):
    """Unmodified output of a single collector run. Raw text/URL are never
    dropped, even after normalization (Coding-Agent Instruction, Phase 0)."""

    source_name: str
    reliability_tier: SourceReliability
    published_at: datetime | None = None
    detected_at: datetime
    title: str | None = None
    raw_text: str
    url: str | None = None
    language: str | None = None
    location_name: str | None = None


class NormalizedSignal(EnergyShieldBaseModel):
    """Common shape every collector output is converted into before it
    reaches the event extraction agent (backend/ingestion/data_normalizer.py)."""

    signal_id: str
    source_name: str
    source_reliability: SourceReliability
    commodity_type: CommodityType | None = None
    published_at: datetime | None = None
    detected_at: datetime
    title: str | None = None
    raw_text: str
    url: str | None = None
    geo_hint: Coordinates | None = None
    corridor_hint: str | None = None
    is_simulated: bool = False
