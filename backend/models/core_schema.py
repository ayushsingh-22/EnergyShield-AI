"""Shared enums, base model, and cross-cutting schemas.

Every other schema module in `backend/models` imports from here so the
frontend, backend, ML, and orchestration tracks share one frozen vocabulary
(Planning Principle #10 in ENERGYSHIELD_IMPLEMENTATION_PLAN.md).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class EnergyShieldBaseModel(BaseModel):
    """Base class for all EnergyShield Pydantic schemas."""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class CommodityType(str, Enum):
    CRUDE_OIL = "CRUDE_OIL"
    LNG = "LNG"
    COAL = "COAL"
    FERTILIZER = "FERTILIZER"
    CRITICAL_MINERALS = "CRITICAL_MINERALS"


class RiskEventType(str, Enum):
    MARITIME_ATTACK = "MARITIME_ATTACK"
    PORT_CLOSURE = "PORT_CLOSURE"
    SANCTION_UPDATE = "SANCTION_UPDATE"
    OPEC_SUPPLY_CUT = "OPEC_SUPPLY_CUT"
    PRICE_SPIKE = "PRICE_SPIKE"
    AIS_REROUTING = "AIS_REROUTING"
    CHOKEPOINT_CONGESTION = "CHOKEPOINT_CONGESTION"
    REFINERY_SUPPLY_RISK = "REFINERY_SUPPLY_RISK"
    EXPORT_RESTRICTION = "EXPORT_RESTRICTION"
    WEATHER_DISRUPTION = "WEATHER_DISRUPTION"
    POLITICAL_INSTABILITY = "POLITICAL_INSTABILITY"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SEVERE = "SEVERE"
    CRITICAL = "CRITICAL"


class SourceReliability(str, Enum):
    OFFICIAL = "OFFICIAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    SIMULATED = "SIMULATED"


class EntityType(str, Enum):
    """Node types shared with the knowledge graph ontology (Phase 3)."""

    SUPPLIER_COUNTRY = "SUPPLIER_COUNTRY"
    SUPPLIER_COMPANY = "SUPPLIER_COMPANY"
    EXPORT_PORT = "EXPORT_PORT"
    SHIPPING_ROUTE = "SHIPPING_ROUTE"
    CHOKEPOINT = "CHOKEPOINT"
    IMPORT_PORT = "IMPORT_PORT"
    REFINERY = "REFINERY"
    STRATEGIC_RESERVE_SITE = "STRATEGIC_RESERVE_SITE"
    CRUDE_GRADE = "CRUDE_GRADE"
    DEMAND_SECTOR = "DEMAND_SECTOR"


class ActionPriority(str, Enum):
    IMMEDIATE = "IMMEDIATE"
    MONITOR = "MONITOR"
    CONTINGENCY = "CONTINGENCY"


class Coordinates(EnergyShieldBaseModel):
    """Point location used by events, digital twin entities, and map layers."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class SourceMetadata(EnergyShieldBaseModel):
    """Provenance block required on every signal per Planning Principle #4.

    Any schema representing something derived from external data should
    embed this rather than re-declaring source/timestamp/confidence fields.
    """

    source_name: str
    source_reliability: SourceReliability
    retrieved_at: datetime
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence_url: str | None = None
    is_simulated: bool = False


class Assumption(EnergyShieldBaseModel):
    """A single explicit, human-readable assumption backing a derived output."""

    description: str
    is_simulated: bool = False


class AuditableMixin(EnergyShieldBaseModel):
    """Fields every recommendation/scenario/risk output must carry.

    Enforces Planning Principles #5 (explainability) and #9 (mark
    simulated values) at the schema level instead of by convention.
    """

    confidence: float = Field(..., ge=0.0, le=1.0)
    assumptions: list[Assumption] = Field(default_factory=list)
    audit_id: str | None = None
