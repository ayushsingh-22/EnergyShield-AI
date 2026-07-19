"""Critical minerals adapter: lithium, cobalt, nickel, graphite, rare earths and EV/battery/defense demand sectors."""

from __future__ import annotations

from typing import Any

from commodities.base_adapter import CommodityAdapter
from models.scenario_schema import ScenarioType

# Illustrative seed set (section 14.6 entities); critical minerals
# ingestion is "roadmap" per `data/seeds/commodity_definitions.yaml`.
# Every entity carries `is_simulated: true` per Planning Principle #9.
_SUPPLY_CHAIN_ENTITIES: list[dict[str, Any]] = [
    {"entity_type": "COMMODITY_GRADE", "entity_id": "MINERAL_LITHIUM", "name": "Lithium", "is_simulated": True},
    {"entity_type": "COMMODITY_GRADE", "entity_id": "MINERAL_COBALT", "name": "Cobalt", "is_simulated": True},
    {"entity_type": "COMMODITY_GRADE", "entity_id": "MINERAL_NICKEL", "name": "Nickel", "is_simulated": True},
    {"entity_type": "COMMODITY_GRADE", "entity_id": "MINERAL_GRAPHITE", "name": "Graphite", "is_simulated": True},
    {"entity_type": "COMMODITY_GRADE", "entity_id": "MINERAL_RARE_EARTHS", "name": "Rare earths", "is_simulated": True},
    {"entity_type": "SUPPLIER_COUNTRY", "entity_id": "MINERAL_MINE_DRC", "name": "DR Congo (mining)", "is_simulated": True},
    {
        "entity_type": "SUPPLIER_COUNTRY",
        "entity_id": "MINERAL_MINE_AUS",
        "name": "Australia (mining)",
        "is_simulated": True,
    },
    {
        "entity_type": "PROCESSING_COUNTRY",
        "entity_id": "MINERAL_PROCESS_CHINA",
        "name": "China (processing/refining)",
        "is_simulated": True,
    },
    {"entity_type": "DEMAND_SECTOR", "entity_id": "MINERAL_DEMAND_EV", "name": "EV manufacturing", "is_simulated": True},
    {
        "entity_type": "DEMAND_SECTOR",
        "entity_id": "MINERAL_DEMAND_BATTERY",
        "name": "Battery manufacturing",
        "is_simulated": True,
    },
    {
        "entity_type": "DEMAND_SECTOR",
        "entity_id": "MINERAL_DEMAND_ELECTRONICS",
        "name": "Electronics manufacturing",
        "is_simulated": True,
    },
    {
        "entity_type": "DEMAND_SECTOR",
        "entity_id": "MINERAL_DEMAND_DEFENSE",
        "name": "Defense manufacturing",
        "is_simulated": True,
    },
]


class CriticalMineralsAdapter(CommodityAdapter):
    commodity_type = "CRITICAL_MINERALS"

    def get_supply_chain_entities(self) -> list[dict[str, Any]]:
        return list(_SUPPLY_CHAIN_ENTITIES)

    def get_risk_features(self, signals: list[dict[str, Any]]) -> dict[str, float]:
        return {"signal_count": float(len(signals)), "supplier_concentration_index": 0.85}

    def get_scenario_templates(self) -> list[str]:
        return [ScenarioType.CRITICAL_MINERAL_EXPORT_RESTRICTION.value]

    def get_recommendation_constraints(self) -> dict[str, Any]:
        return {
            "quality_constraint": "mineral purity/grade matching manufacturing specification",
            "storage_constraint": "no strategic reserve; buffer limited to manufacturer inventory",
            "transport_constraint": "midstream processing bottleneck outside India, not just mine-to-port logistics",
            "substitution_constraint": (
                "supplier concentration is high and substitution feasibility is simulated pending "
                "verified alternate-source processing capacity"
            ),
        }
