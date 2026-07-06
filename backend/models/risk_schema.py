"""RiskScore schema (Phase 5 corridor and supplier risk scoring engine)."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from models.core_schema import (
    CommodityType,
    EnergyShieldBaseModel,
    EntityType,
    RiskLevel,
)


class RiskScore(EnergyShieldBaseModel):
    """Matches the "Risk Score Output Schema" in Phase 5 of the implementation plan."""

    entity_id: str
    entity_type: EntityType
    commodity_type: CommodityType
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    previous_score: float | None = Field(default=None, ge=0, le=100)
    delta: float | None = None
    top_drivers: list[str] = Field(default_factory=list)
    evidence_event_ids: list[str] = Field(default_factory=list)
    updated_at: datetime
