"""Procurement and SPR recommendation schemas (Phase 7)."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from backend.models.core_schema import (
    ActionPriority,
    Assumption,
    CommodityType,
    EnergyShieldBaseModel,
    RiskLevel,
)


class ProcurementOption(EnergyShieldBaseModel):
    """One ranked entry in a recommendation's option list."""

    rank: int = Field(..., ge=1)
    supplier: str
    route: str
    estimated_delay_days: float = Field(..., ge=0)
    cost_impact_percent: float
    risk_level: RiskLevel
    feasibility_score: float = Field(..., ge=0.0, le=1.0)
    reason: str
    action_priority: ActionPriority = ActionPriority.MONITOR


class SprPlan(EnergyShieldBaseModel):
    """Strategic petroleum reserve drawdown recommendation."""

    drawdown_required: bool
    start_day: int | None = Field(default=None, ge=0)
    drawdown_percent: float | None = Field(default=None, ge=0, le=100)
    reason: str


class Recommendation(EnergyShieldBaseModel):
    """Matches the "Recommendation Output Schema" in Phase 7 of the
    implementation plan. Every field required by Planning Principle #5
    (assumptions + explanation) and the audit trail (Phase 11) is present."""

    recommendation_id: str
    scenario_id: str
    commodity_type: CommodityType
    ranked_options: list[ProcurementOption] = Field(default_factory=list)
    spr_plan: SprPlan | None = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    assumptions: list[Assumption] = Field(default_factory=list)
    audit_id: str | None = None
    created_at: datetime
