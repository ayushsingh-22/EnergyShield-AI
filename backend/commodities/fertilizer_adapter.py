"""Fertilizer supply chain adapter: urea/DAP/MOP/ammonia, feedstocks, and seasonal agricultural demand."""

from __future__ import annotations

from typing import Any

from commodities.base_adapter import CommodityAdapter
from models.scenario_schema import ScenarioType

# Illustrative seed set (section 14.5 entities); fertilizer ingestion is
# "roadmap" per `data/seeds/commodity_definitions.yaml`. Every entity
# carries `is_simulated: true` per Planning Principle #9.
_SUPPLY_CHAIN_ENTITIES: list[dict[str, Any]] = [
    {"entity_type": "COMMODITY_GRADE", "entity_id": "FERT_UREA", "name": "Urea", "is_simulated": True},
    {"entity_type": "COMMODITY_GRADE", "entity_id": "FERT_DAP", "name": "DAP", "is_simulated": True},
    {"entity_type": "COMMODITY_GRADE", "entity_id": "FERT_MOP", "name": "MOP", "is_simulated": True},
    {"entity_type": "FEEDSTOCK", "entity_id": "FERT_FEED_NATGAS", "name": "Natural gas", "is_simulated": True},
    {"entity_type": "FEEDSTOCK", "entity_id": "FERT_FEED_PHOSPHATE", "name": "Phosphate rock", "is_simulated": True},
    {"entity_type": "FEEDSTOCK", "entity_id": "FERT_FEED_POTASH", "name": "Potash", "is_simulated": True},
    {"entity_type": "SUPPLIER_COUNTRY", "entity_id": "FERT_SUP_CANADA", "name": "Canada", "is_simulated": True},
    {"entity_type": "SUPPLIER_COUNTRY", "entity_id": "FERT_SUP_MOROCCO", "name": "Morocco", "is_simulated": True},
    {
        "entity_type": "IMPORT_PORT",
        "entity_id": "FERT_PRT_KANDLA",
        "name": "Kandla Fertilizer Terminal",
        "country": "India",
        "is_simulated": True,
    },
    {
        "entity_type": "DEMAND_SECTOR",
        "entity_id": "FERT_DEMAND_KHARIF",
        "name": "Kharif season agricultural demand",
        "is_simulated": True,
    },
    {
        "entity_type": "DEMAND_SECTOR",
        "entity_id": "FERT_DEMAND_RABI",
        "name": "Rabi season agricultural demand",
        "is_simulated": True,
    },
]


class FertilizerAdapter(CommodityAdapter):
    commodity_type = "FERTILIZER"

    def get_supply_chain_entities(self) -> list[dict[str, Any]]:
        return list(_SUPPLY_CHAIN_ENTITIES)

    def get_risk_features(self, signals: list[dict[str, Any]]) -> dict[str, float]:
        return {"signal_count": float(len(signals)), "feedstock_price_pressure_index": 0.5}

    def get_scenario_templates(self) -> list[str]:
        return [ScenarioType.FERTILIZER_FEEDSTOCK_SHOCK.value]

    def get_recommendation_constraints(self) -> dict[str, Any]:
        return {
            "quality_constraint": "nutrient grade matching (N-P-K composition)",
            "storage_constraint": "port and distribution-node stockpile capacity ahead of the sowing season",
            "transport_constraint": "domestic distribution network capacity to reach agricultural demand nodes in season",
            "substitution_constraint": (
                "seasonal (Kharif/Rabi) demand timing constrains how quickly an alternate supplier can substitute"
            ),
        }
