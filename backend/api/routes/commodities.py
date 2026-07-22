"""Commodity selection and commodity metadata endpoints (Phase 14 multi-commodity platform expansion)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException

from api.routes.recommendations import _recommendation_service
from api.routes.scenarios import service as scenario_service
from commodities.base_adapter import CommodityAdapter
from commodities.coal_adapter import CoalAdapter
from commodities.critical_minerals_adapter import CriticalMineralsAdapter
from commodities.crude_oil_adapter import CrudeOilAdapter
from commodities.fertilizer_adapter import FertilizerAdapter
from commodities.lng_adapter import LngAdapter
from models.commodity_schema import CommodityDefinition
from models.core_schema import Assumption, CommodityType, EntityType, RiskLevel
from models.risk_schema import RiskScore
from models.scenario_schema import ScenarioRequest, ScenarioResult
from reports.formatting import humanize
from services.digital_twin_service import DigitalTwinService
from services.risk_service import RiskService

router = APIRouter(prefix="/api/v1/commodities", tags=["commodities"])
_risk_service = RiskService()
_digital_twin = DigitalTwinService()
_digital_twin.load_seed_data()
_DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "seeds" / "commodity_definitions.yaml"

# One `CommodityAdapter` per commodity (Phase 14, section 14.2) - the risk
# engine, scenario engine, and recommendation agents call these adapters'
# four methods rather than branching on commodity type internally
# (docs/MULTI_COMMODITY_ROADMAP.md).
_ADAPTERS: dict[CommodityType, CommodityAdapter] = {
    CommodityType.CRUDE_OIL: CrudeOilAdapter(_digital_twin),
    CommodityType.LNG: LngAdapter(),
    CommodityType.COAL: CoalAdapter(),
    CommodityType.FERTILIZER: FertilizerAdapter(),
    CommodityType.CRITICAL_MINERALS: CriticalMineralsAdapter(),
}


def _scenario_templates_for(commodity_type: CommodityType) -> list[str]:
    return _ADAPTERS[commodity_type].get_scenario_templates()


def _load_definitions() -> dict[CommodityType, CommodityDefinition]:
    payload = yaml.safe_load(_DATA_FILE.read_text())
    definitions: dict[CommodityType, CommodityDefinition] = {}
    for item in payload.get("commodities", []):
        commodity_type = CommodityType(item["commodity_type"])
        definitions[commodity_type] = CommodityDefinition(
            commodity_type=commodity_type,
            display_name=humanize(item["commodity_type"]),
            unit={
                CommodityType.CRUDE_OIL: "barrel",
                CommodityType.LNG: "mmbtu",
                CommodityType.COAL: "tonne",
                CommodityType.FERTILIZER: "tonne",
                CommodityType.CRITICAL_MINERALS: "tonne",
            }[commodity_type],
            demand_sector_ids=item.get("key_risks", []),
            risk_parameters={"status_weight": 1.0 if item.get("status") == "implemented" else 0.5},
            scenario_template_ids=_scenario_templates_for(commodity_type),
        )
    return definitions


def _risk_level_for(score: float) -> RiskLevel:
    if score >= 80:
        return RiskLevel.CRITICAL
    if score >= 60:
        return RiskLevel.SEVERE
    if score >= 40:
        return RiskLevel.HIGH
    if score >= 20:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _roadmap_risk(commodity_type: CommodityType) -> list[RiskScore]:
    """Roadmap-commodity structural risk, derived from the adapter's own
    `get_risk_features` (a real per-commodity number) rather than a fixed
    constant, so LNG/coal/fertilizer/critical-minerals each read
    differently and honestly reflect their supplier-concentration index.

    These commodities have no live ingestion yet (`commodity_definitions.yaml`
    marks them "roadmap"), so the score is a structural-concentration
    estimate, flagged simulated - not a live event-driven score like crude
    oil's. When their ingestion streams are built, this endpoint routes
    through the real `RiskService` the same way crude oil already does."""
    adapter = _ADAPTERS[commodity_type]
    features = adapter.get_risk_features(signals=[])
    concentration = float(features.get("supplier_concentration_index", 0.5))
    # Supplier concentration is the dominant structural vulnerability for a
    # commodity with no live signal feed: map its 0..1 index onto the same
    # 0..100 band the risk engine uses.
    score = round(min(100.0, max(0.0, concentration * 100.0)), 1)
    entity_count = len(adapter.get_supply_chain_entities())
    top_drivers = [
        f"Structural supplier-concentration index {concentration:.2f} across {entity_count} scaffolded entities.",
    ]

    # Coal/LNG have a real live price feed wired in (World Bank Pink Sheet /
    # EIA Henry Hub - see ingestion/coal_price_collector.py and
    # ingestion/lng_price_collector.py) even though their supply-chain
    # entities above are still a scaffold; surface that real signal when present.
    has_price_signal = "price_anomaly_detected" in features
    price_anomaly = bool(features.get("price_anomaly_detected", 0.0))
    if has_price_signal:
        if price_anomaly:
            score = round(min(100.0, score + 15.0), 1)
            top_drivers.append("Live benchmark price move exceeded the anomaly threshold this period.")
        else:
            top_drivers.append("Live benchmark price feed active; no anomaly threshold breached this period.")
    top_drivers.append("Roadmap commodity: supply-chain entities are a structural scaffold, not live ingestion streams.")

    assumption_text = (
        f"{commodity_type.value} supply-chain entities are illustrative and not yet backed by live ingestion; "
        "risk score combines a structural supplier-concentration estimate with a live benchmark price signal."
        if has_price_signal
        else (
            f"{commodity_type.value} has no live signal ingestion yet; risk is a structural "
            "supplier-concentration estimate, not an event-driven live score."
        )
    )

    return [
        RiskScore(
            entity_id=f"{commodity_type.value}_GLOBAL",
            entity_type=EntityType.DEMAND_SECTOR,
            commodity_type=commodity_type,
            risk_score=score,
            risk_level=_risk_level_for(score),
            previous_score=None,
            delta=None,
            top_drivers=top_drivers,
            evidence_event_ids=[],
            confidence=0.6 if has_price_signal else 0.5,
            assumptions=[Assumption(description=assumption_text, is_simulated=not has_price_signal)],
            audit_id=f"AUD-{commodity_type.value}-ROADMAP",
            updated_at=datetime.now(timezone.utc),
        )
    ]


@router.get("", response_model=list[CommodityDefinition])
def list_commodities() -> list[CommodityDefinition]:
    return list(_load_definitions().values())


@router.get("/{commodity_type}/entities")
def get_commodity_entities(commodity_type: CommodityType) -> dict[str, object]:
    entities = _ADAPTERS[commodity_type].get_supply_chain_entities()
    return {
        "commodity_type": commodity_type,
        "entity_count": len(entities),
        "entities": entities,
    }


@router.get("/{commodity_type}/risk", response_model=list[RiskScore])
def get_commodity_risk(commodity_type: CommodityType) -> list[RiskScore]:
    if commodity_type is CommodityType.CRUDE_OIL:
        return [*_risk_service.get_corridors(), *_risk_service.get_suppliers()]
    return _roadmap_risk(commodity_type)


@router.get("/{commodity_type}/scenarios")
def get_commodity_scenarios(commodity_type: CommodityType) -> list[str]:
    return _scenario_templates_for(commodity_type)


@router.post("/{commodity_type}/scenarios/run", response_model=ScenarioResult)
def run_commodity_scenario(commodity_type: CommodityType, request: ScenarioRequest) -> ScenarioResult:
    if request.commodity_type != commodity_type:
        request = request.model_copy(update={"commodity_type": commodity_type})
    return scenario_service.run_scenario(request)


@router.get("/{commodity_type}/recommendations/{scenario_id}")
def get_commodity_recommendation(commodity_type: CommodityType, scenario_id: str):
    scenario = scenario_service.get_scenario(scenario_id)
    if scenario is None or scenario.commodity_type != commodity_type:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found for commodity '{commodity_type}'")
    return _recommendation_service.get_or_create_for_scenario(scenario)
