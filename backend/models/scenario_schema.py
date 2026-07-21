"""Scenario request and output schemas (Phase 6 disruption scenario modeller)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from models.core_schema import (
    Assumption,
    CommodityType,
    EnergyShieldBaseModel,
    RiskLevel,
)


class ScenarioType(str, Enum):
    HORMUZ_PARTIAL_CLOSURE = "HORMUZ_PARTIAL_CLOSURE"
    RED_SEA_SHIPPING_DISRUPTION = "RED_SEA_SHIPPING_DISRUPTION"
    OPEC_SUPPLY_CUT = "OPEC_SUPPLY_CUT"
    SANCTIONS_SHOCK = "SANCTIONS_SHOCK"
    PORT_CONGESTION = "PORT_CONGESTION"
    # Phase 14 multi-commodity templates
    LNG_SUPPLY_SHOCK = "LNG_SUPPLY_SHOCK"
    COAL_IMPORT_DISRUPTION = "COAL_IMPORT_DISRUPTION"
    FERTILIZER_FEEDSTOCK_SHOCK = "FERTILIZER_FEEDSTOCK_SHOCK"
    CRITICAL_MINERAL_EXPORT_RESTRICTION = "CRITICAL_MINERAL_EXPORT_RESTRICTION"


class ScenarioRequest(EnergyShieldBaseModel):
    """POST body for /api/v1/scenarios/run."""

    scenario_type: ScenarioType
    commodity_type: CommodityType
    duration_days: int = Field(..., gt=0)
    severity: RiskLevel
    affected_entities: list[str] = Field(default_factory=list)
    manual_overrides: dict[str, float] = Field(default_factory=dict)


class AffectedRefinery(EnergyShieldBaseModel):
    refinery_id: str
    exposure_level: RiskLevel
    reason: str


class ScenarioResult(EnergyShieldBaseModel):
    """Matches the "Scenario Output Schema" in Phase 6 of the implementation plan."""

    scenario_id: str
    scenario_type: ScenarioType
    commodity_type: CommodityType
    duration_days: int
    supply_at_risk_percent: float = Field(..., ge=0, le=100)
    estimated_delay_days: float = Field(..., ge=0)
    freight_cost_impact_percent: float = Field(..., ge=0, le=300)
    fuel_price_increase_percent: float = Field(..., ge=0)
    gdp_impact_percent: float = Field(...)
    affected_refineries: list[AffectedRefinery] = Field(default_factory=list)
    recommended_action_required: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    assumptions: list[Assumption] = Field(default_factory=list)
    created_at: datetime
