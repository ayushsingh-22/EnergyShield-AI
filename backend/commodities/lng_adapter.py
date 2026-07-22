"""LNG supply chain adapter: export terminals, LNG vessel routes, regasification terminals, demand sectors."""

from __future__ import annotations

from typing import Any

from commodities.base_adapter import CommodityAdapter
from ingestion.lng_price_collector import LngPriceCollector
from models.scenario_schema import ScenarioType

# Illustrative seed set (section 14.3 entities) - real LNG supplier/
# terminal ingestion is not built yet (`data/seeds/commodity_definitions.yaml`
# marks LNG as "roadmap"). Every entity carries `is_simulated: true` per
# Planning Principle #9, same convention `data/seeds/demo_disruption_cases.json`
# uses for Phase 13.
_SUPPLY_CHAIN_ENTITIES: list[dict[str, Any]] = [
    {"entity_type": "SUPPLIER_COUNTRY", "entity_id": "LNG_SUP_QATAR", "name": "Qatar", "is_simulated": True},
    {"entity_type": "SUPPLIER_COUNTRY", "entity_id": "LNG_SUP_AUS", "name": "Australia", "is_simulated": True},
    {"entity_type": "SUPPLIER_COUNTRY", "entity_id": "LNG_SUP_USA", "name": "United States", "is_simulated": True},
    {
        "entity_type": "EXPORT_TERMINAL",
        "entity_id": "LNG_TERM_RASGAS",
        "name": "Ras Laffan LNG Terminal",
        "country": "Qatar",
        "is_simulated": True,
    },
    {
        "entity_type": "SHIPPING_ROUTE",
        "entity_id": "LNG_RT_QATAR_INDIA",
        "name": "Ras Laffan to Dahej",
        "is_simulated": True,
    },
    {
        "entity_type": "REGAS_TERMINAL",
        "entity_id": "LNG_REGAS_DAHEJ",
        "name": "Dahej Regasification Terminal",
        "country": "India",
        "is_simulated": True,
    },
    {
        "entity_type": "REGAS_TERMINAL",
        "entity_id": "LNG_REGAS_HAZIRA",
        "name": "Hazira Regasification Terminal",
        "country": "India",
        "is_simulated": True,
    },
    {"entity_type": "DEMAND_SECTOR", "entity_id": "LNG_DEMAND_POWER", "name": "Power generation", "is_simulated": True},
    {
        "entity_type": "DEMAND_SECTOR",
        "entity_id": "LNG_DEMAND_CITY_GAS",
        "name": "City gas distribution",
        "is_simulated": True,
    },
    {
        "entity_type": "DEMAND_SECTOR",
        "entity_id": "LNG_DEMAND_FERTILIZER",
        "name": "Fertilizer feedstock",
        "is_simulated": True,
    },
]


class LngAdapter(CommodityAdapter):
    commodity_type = "LNG"

    def __init__(self, price_collector: LngPriceCollector | None = None):
        self._price_collector = price_collector or LngPriceCollector()

    def get_supply_chain_entities(self) -> list[dict[str, Any]]:
        return list(_SUPPLY_CHAIN_ENTITIES)

    def get_risk_features(self, signals: list[dict[str, Any]]) -> dict[str, float]:
        # Supply-chain entities above are still an illustrative scaffold
        # (no real supplier/terminal-share ingestion yet), but the price
        # signal itself is real: Henry Hub natural gas via EIA, used as an
        # LNG feedstock proxy (`ingestion/lng_price_collector.py`).
        price_records = self._price_collector.fetch()
        is_price_anomaly = any("Anomaly" in (record.title or "") for record in price_records)
        return {
            "signal_count": float(len(signals)),
            "supplier_concentration_index": 0.65,
            "price_anomaly_detected": 1.0 if is_price_anomaly else 0.0,
        }

    def get_scenario_templates(self) -> list[str]:
        return [ScenarioType.LNG_SUPPLY_SHOCK.value]

    def get_recommendation_constraints(self) -> dict[str, Any]:
        return {
            "quality_constraint": "calorific value / regasification terminal compatibility",
            "storage_constraint": "no strategic LNG reserve; limited terminal buffer capacity",
            "transport_constraint": "LNG carrier (charter market) availability",
            "substitution_constraint": (
                "spot cargo diversion depends on charter market availability, which is not directly observed"
            ),
        }
