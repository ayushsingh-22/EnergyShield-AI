"""Pydantic schemas for suppliers, ports, routes, refineries, and SPR sites (Phase 2 digital twin)."""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import Field

from models.core_schema import (
    CommodityType,
    Coordinates,
    EnergyShieldBaseModel,
    RiskLevel,
)


class DigitalTwinEntityBase(EnergyShieldBaseModel):
    """Base class for all spatial and logical entities in the Digital Twin."""
    id: str = Field(alias="entity_id")
    name: str
    coordinates: Optional[Coordinates] = None
    commodity_support: List[CommodityType] = Field(default_factory=lambda: [CommodityType.CRUDE_OIL])
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_simulated: bool = False
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class Commodity(DigitalTwinEntityBase):
    """A tracked commodity in the system (e.g. Crude Oil, LNG)."""
    pass


class SupplierCountry(DigitalTwinEntityBase):
    """A crude-oil supplier country and its baseline import exposure to India."""
    country: str
    region: str
    import_share_percent: float = Field(..., ge=0, le=100)
    default_export_port_id: Optional[str] = None
    default_shipping_route_id: Optional[str] = None
    risk_metadata_placeholder: Dict[str, Any] = Field(default_factory=dict)
    data_source: str = "estimated"
    supported_crude_grade_ids: List[str] = Field(default_factory=list)


class SupplierCompany(DigitalTwinEntityBase):
    """Optional entity representing a specific supplier company (e.g. Saudi Aramco)."""
    country: str
    parent_company: Optional[str] = None


class ExportPort(DigitalTwinEntityBase):
    """An export port used by a supplier country."""
    country: str
    connected_supplier_ids: List[str] = Field(default_factory=list)
    capacity_mmt: Optional[float] = Field(default=None, ge=0, description="Estimated capacity in MMT")


class ShippingRoute(DigitalTwinEntityBase):
    """A shipping route linking an export port to an import port."""
    origin_port_id: str
    destination_port_id: str
    affected_chokepoint_ids: List[str] = Field(default_factory=list)
    distance_km: Optional[float] = Field(default=None, ge=0)
    estimated_transit_days: Optional[float] = Field(default=None, ge=0)
    route_geometry: Optional[Dict[str, Any]] = Field(default=None, description="GeoJSON LineString coords")
    route_status: str = "OPEN"
    route_type: str = "MARITIME"
    risk_level: RiskLevel = RiskLevel.LOW


class Chokepoint(DigitalTwinEntityBase):
    """A maritime chokepoint (e.g. Hormuz, Bab el-Mandeb, Suez)."""
    country_region: str
    importance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    connected_route_ids: List[str] = Field(default_factory=list)
    geometry: Optional[Dict[str, Any]] = Field(default=None, description="GeoJSON Polygon")
    risk_level: RiskLevel = RiskLevel.LOW


class ImportPort(DigitalTwinEntityBase):
    """An Indian crude import port."""
    state: str
    country: str = "India"
    connected_refinery_ids: List[str] = Field(default_factory=list)
    capacity_mmt: Optional[float] = Field(default=None, ge=0)


class Refinery(DigitalTwinEntityBase):
    """An Indian refinery fed by one or more import ports."""
    owner: str = Field(default="public")
    capacity_bpd: Optional[float] = Field(default=None, ge=0)
    connected_import_port_ids: List[str] = Field(default_factory=list)
    accepted_crude_grade_ids: List[str] = Field(default_factory=list)
    location_name: str
    operational_status: str = "ONLINE"
    estimated_flexibility_score: float = Field(default=0.5, ge=0.0, le=1.0)


class StrategicReserveSite(DigitalTwinEntityBase):
    """A strategic petroleum reserve (SPR) storage site."""
    capacity_mmbbl: Optional[float] = Field(default=None, ge=0)
    supported_refinery_ids: List[str] = Field(default_factory=list)
    drawdown_priority: int = 1


class CrudeGrade(DigitalTwinEntityBase):
    """A crude oil grade (e.g. Arab Light, WTI, Urals)."""
    api_gravity: Optional[float] = None
    sulfur_content_percent: Optional[float] = Field(default=None, ge=0)


class DemandSector(DigitalTwinEntityBase):
    """A downstream demand sector consuming a commodity."""
    demand_share_percent: Optional[float] = Field(default=None, ge=0, le=100)
