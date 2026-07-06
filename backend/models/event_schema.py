"""Risk event and extraction schemas (Phase 4 event extraction agent)."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from models.core_schema import (
    CommodityType,
    Coordinates,
    EnergyShieldBaseModel,
    RiskEventType,
    SourceReliability,
)


class EventEvidence(EnergyShieldBaseModel):
    """One corroborating piece of evidence for a risk event."""

    source_name: str
    url: str | None = None
    excerpt: str | None = None


class RiskEvent(EnergyShieldBaseModel):
    """Structured output of the event extraction agent.

    Matches the "Risk Event Output Schema" in
    ENERGYSHIELD_IMPLEMENTATION_PLAN.md Phase 4.
    """

    event_id: str
    event_type: RiskEventType
    commodity_type: CommodityType
    title: str
    summary: str
    published_at: datetime | None = None
    detected_at: datetime
    source_name: str
    source_reliability: SourceReliability
    location_name: str | None = None
    coordinates: Coordinates | None = None
    affected_entities: list[str] = Field(default_factory=list)
    severity: int = Field(..., ge=1, le=5)
    confidence: float = Field(..., ge=0.0, le=1.0)
    scenario_triggers: list[str] = Field(default_factory=list)
    evidence_urls: list[str] = Field(default_factory=list)
    is_simulated: bool = False


class ExtractionResult(EnergyShieldBaseModel):
    """Wraps a RiskEvent with the extraction pipeline's own diagnostics so
    failures are visible instead of silently dropped (Coding-Agent
    Instruction: "Any LLM-generated output must have deterministic
    fallback logic")."""

    signal_id: str
    event: RiskEvent | None
    extraction_method: str = Field(
        ..., description='e.g. "llm", "rule_based_fallback", "official_alert_direct"'
    )
    succeeded: bool
    error_message: str | None = None
