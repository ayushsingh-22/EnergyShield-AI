"""Coal supply chain adapter: export ports, shipping routes, rail corridors, power/industrial demand nodes."""

from __future__ import annotations

from typing import Any

from commodities.base_adapter import CommodityAdapter
from models.scenario_schema import ScenarioType

# Illustrative seed set (section 14.4 entities); coal ingestion is
# "roadmap" per `data/seeds/commodity_definitions.yaml`. Every entity
# carries `is_simulated: true` per Planning Principle #9.
_SUPPLY_CHAIN_ENTITIES: list[dict[str, Any]] = [
    {"entity_type": "SUPPLIER_COUNTRY", "entity_id": "COAL_SUP_AUS", "name": "Australia", "is_simulated": True},
    {"entity_type": "SUPPLIER_COUNTRY", "entity_id": "COAL_SUP_IDN", "name": "Indonesia", "is_simulated": True},
    {"entity_type": "SUPPLIER_COUNTRY", "entity_id": "COAL_SUP_ZAF", "name": "South Africa", "is_simulated": True},
    {
        "entity_type": "EXPORT_PORT",
        "entity_id": "COAL_PRT_NEWCASTLE",
        "name": "Newcastle Coal Terminal",
        "country": "Australia",
        "is_simulated": True,
    },
    {
        "entity_type": "SHIPPING_ROUTE",
        "entity_id": "COAL_RT_AUS_INDIA",
        "name": "Newcastle to Paradip",
        "is_simulated": True,
    },
    {
        "entity_type": "IMPORT_PORT",
        "entity_id": "COAL_PRT_PARADIP",
        "name": "Paradip Coal Terminal",
        "country": "India",
        "is_simulated": True,
    },
    {
        "entity_type": "RAIL_CORRIDOR",
        "entity_id": "COAL_RAIL_PARADIP_ODISHA",
        "name": "Paradip to Odisha power belt rail corridor",
        "is_simulated": True,
    },
    {"entity_type": "DEMAND_SECTOR", "entity_id": "COAL_DEMAND_POWER", "name": "Power generation", "is_simulated": True},
    {
        "entity_type": "DEMAND_SECTOR",
        "entity_id": "COAL_DEMAND_STEEL",
        "name": "Steel and industrial",
        "is_simulated": True,
    },
]


class CoalAdapter(CommodityAdapter):
    commodity_type = "COAL"

    def get_supply_chain_entities(self) -> list[dict[str, Any]]:
        return list(_SUPPLY_CHAIN_ENTITIES)

    def get_risk_features(self, signals: list[dict[str, Any]]) -> dict[str, float]:
        return {"signal_count": float(len(signals)), "rail_bottleneck_index": 0.4}

    def get_scenario_templates(self) -> list[str]:
        return [ScenarioType.COAL_IMPORT_DISRUPTION.value]

    def get_recommendation_constraints(self) -> dict[str, Any]:
        return {
            "quality_constraint": "coal grade/calorific value matching power plant boiler design",
            "storage_constraint": "port and power-plant stockpile capacity",
            "transport_constraint": "rail corridor capacity from port to inland demand",
            "substitution_constraint": "alternate supplier must clear export-country port and weather disruption risk",
        }
