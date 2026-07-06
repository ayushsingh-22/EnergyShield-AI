"""Pydantic schemas for suppliers, ports, routes, refineries, and SPR sites (Phase 2 digital twin)."""

from __future__ import annotations

from pydantic import Field

from backend.models.core_schema import (
    CommodityType,
    Coordinates,
    EnergyShieldBaseModel,
    RiskLevel,
)


class SupplierCountry(EnergyShieldBaseModel):
    """A crude-oil supplier country and its baseline import exposure to India."""

    entity_id: str
    name: str
    region: str
    commodity_types: list[CommodityType] = Field(default_factory=list)
    import_share_percent: float = Field(..., ge=0, le=100)
    default_route_id: str | None = None
    is_estimated: bool = True


class ExportPort(EnergyShieldBaseModel):
    """An export port used by a supplier country."""

    entity_id: str
    name: str
    country: str
    supplier_id: str | None = None
    coordinates: Coordinates | None = None


class ShippingRoute(EnergyShieldBaseModel):
    """A line-string shipping route linking an export port to an import port."""

    entity_id: str
    name: str
    origin_port_id: str
    destination_port_id: str
    chokepoint_ids: list[str] = Field(default_factory=list)
    distance_km: float | None = Field(default=None, ge=0)
    typical_transit_days: float | None = Field(default=None, ge=0)
    risk_level: RiskLevel = RiskLevel.LOW


class Chokepoint(EnergyShieldBaseModel):
    """A maritime chokepoint polygon or bounding box (e.g. Hormuz, Bab el-Mandeb, Suez)."""

    entity_id: str
    name: str
    region: str
    coordinates: Coordinates | None = None
    risk_level: RiskLevel = RiskLevel.LOW


class ImportPort(EnergyShieldBaseModel):
    """An Indian crude import port."""

    entity_id: str
    name: str
    country: str = "India"
    coordinates: Coordinates | None = None
    annual_capacity_mmt: float | None = Field(default=None, ge=0)


class Refinery(EnergyShieldBaseModel):
    """An Indian refinery fed by one or more import ports."""

    entity_id: str
    name: str
    import_port_ids: list[str] = Field(default_factory=list)
    coordinates: Coordinates | None = None
    capacity_bpd: float | None = Field(default=None, ge=0)
    owner_type: str = Field(default="public", description='"public" or "private"')
    crude_grade_ids: list[str] = Field(
        default_factory=list, description="Grades this refinery can process (simulated unless cited)."
    )
    is_simulated: bool = False


class StrategicReserveSite(EnergyShieldBaseModel):
    """A strategic petroleum reserve (SPR) storage site."""

    entity_id: str
    name: str
    coordinates: Coordinates | None = None
    capacity_mmbbl: float | None = Field(default=None, ge=0)
    drawdown_rate_bpd: float | None = Field(default=None, ge=0)
    supports_refinery_ids: list[str] = Field(default_factory=list)
    is_simulated: bool = False


class CrudeGrade(EnergyShieldBaseModel):
    """A crude oil grade (e.g. Arab Light, WTI, Urals)."""

    entity_id: str
    name: str
    api_gravity: float | None = None
    sulfur_content_percent: float | None = Field(default=None, ge=0)


class DemandSector(EnergyShieldBaseModel):
    """A downstream demand sector consuming a commodity (e.g. transport, power, petrochemical)."""

    entity_id: str
    name: str
    commodity_type: CommodityType
    demand_share_percent: float | None = Field(default=None, ge=0, le=100)
