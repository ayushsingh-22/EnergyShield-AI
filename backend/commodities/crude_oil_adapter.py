"""Crude oil commodity adapter wrapping the existing India crude-oil MVP logic."""

from __future__ import annotations

from typing import Any

from commodities.base_adapter import CommodityAdapter
from models.scenario_schema import ScenarioType
from services.digital_twin_service import DigitalTwinService


def _load_default_digital_twin() -> DigitalTwinService:
    digital_twin = DigitalTwinService()
    digital_twin.load_seed_data()
    return digital_twin


class CrudeOilAdapter(CommodityAdapter):
    """Wraps the existing Phase 2-7 crude-oil MVP (section 14.2, step 2:
    "create crude-oil adapter from existing MVP logic") so it satisfies
    the same `CommodityAdapter` interface every other commodity uses,
    without duplicating any digital-twin/risk/scenario logic."""

    commodity_type = "CRUDE_OIL"

    def __init__(self, digital_twin: DigitalTwinService | None = None):
        self._digital_twin = digital_twin or _load_default_digital_twin()

    def get_supply_chain_entities(self) -> list[dict[str, Any]]:
        twin = self._digital_twin
        entities: list[dict[str, Any]] = []
        entities += [{"entity_type": "SUPPLIER_COUNTRY", **s.model_dump(by_alias=True)} for s in twin.get_suppliers()]
        entities += [{"entity_type": "SHIPPING_ROUTE", **r.model_dump(by_alias=True)} for r in twin.get_routes()]
        entities += [{"entity_type": "CHOKEPOINT", **c.model_dump(by_alias=True)} for c in twin.get_chokepoints()]
        entities += [{"entity_type": "IMPORT_PORT", **p.model_dump(by_alias=True)} for p in twin.get_import_ports()]
        entities += [{"entity_type": "REFINERY", **r.model_dump(by_alias=True)} for r in twin.get_refineries()]
        entities += [{"entity_type": "STRATEGIC_RESERVE_SITE", **s.model_dump(by_alias=True)} for s in twin.get_spr_sites()]
        return entities

    def get_risk_features(self, signals: list[dict[str, Any]]) -> dict[str, float]:
        exposure = self._digital_twin.get_exposure_summary()
        return {
            "total_supplier_exposure_percent": exposure["total_supplier_exposure_percent"],
            "signal_count": float(len(signals)),
        }

    def get_scenario_templates(self) -> list[str]:
        return [
            ScenarioType.HORMUZ_PARTIAL_CLOSURE.value,
            ScenarioType.RED_SEA_SHIPPING_DISRUPTION.value,
            ScenarioType.OPEC_SUPPLY_CUT.value,
            ScenarioType.SANCTIONS_SHOCK.value,
            ScenarioType.PORT_CONGESTION.value,
        ]

    def get_recommendation_constraints(self) -> dict[str, Any]:
        return {
            "quality_constraint": "refinery-grade compatibility (API gravity / sulfur content)",
            "storage_constraint": "strategic petroleum reserve drawdown limits",
            "transport_constraint": "tanker availability and chokepoint transit risk",
            "substitution_constraint": "alternate supplier must produce a compatible crude grade",
        }
