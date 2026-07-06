"""Generic commodity, grade, demand sector, and supply chain schemas (Phase 14 multi-commodity expansion)."""

from __future__ import annotations

from pydantic import Field

from backend.models.core_schema import CommodityType, EnergyShieldBaseModel


class Commodity(EnergyShieldBaseModel):
    """A single commodity instance tracked by the platform."""

    commodity_type: CommodityType
    name: str
    unit: str = Field(..., description='e.g. "barrel", "tonne", "mmbtu".')
    grade_ids: list[str] = Field(default_factory=list)


class CommodityDefinition(EnergyShieldBaseModel):
    """Static commodity metadata and risk parameters (data/seeds/commodity_definitions.yaml)."""

    commodity_type: CommodityType
    display_name: str
    unit: str
    demand_sector_ids: list[str] = Field(default_factory=list)
    risk_parameters: dict[str, float] = Field(default_factory=dict)
    scenario_template_ids: list[str] = Field(default_factory=list)
