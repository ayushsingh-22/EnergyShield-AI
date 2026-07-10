"""Commodity selection and commodity metadata endpoints (Phase 14 multi-commodity platform expansion)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException

from api.routes.recommendations import _recommendation_service
from api.routes.scenarios import service as scenario_service
from models.commodity_schema import CommodityDefinition
from models.core_schema import CommodityType, EntityType, RiskLevel
from models.risk_schema import RiskScore
from models.scenario_schema import ScenarioRequest, ScenarioResult, ScenarioType
from services.digital_twin_service import DigitalTwinService
from services.risk_service import RiskService

router = APIRouter(prefix="/api/v1/commodities", tags=["commodities"])
_risk_service = RiskService()
_digital_twin = DigitalTwinService()
_digital_twin.load_seed_data()
_DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "seeds" / "commodity_definitions.yaml"


def _scenario_templates_for(commodity_type: CommodityType) -> list[str]:
    mapping = {
        CommodityType.CRUDE_OIL: [
            ScenarioType.HORMUZ_PARTIAL_CLOSURE.value,
            ScenarioType.RED_SEA_SHIPPING_DISRUPTION.value,
            ScenarioType.OPEC_SUPPLY_CUT.value,
            ScenarioType.SANCTIONS_SHOCK.value,
            ScenarioType.PORT_CONGESTION.value,
        ],
        CommodityType.LNG: [ScenarioType.LNG_SUPPLY_SHOCK.value],
        CommodityType.COAL: [ScenarioType.COAL_IMPORT_DISRUPTION.value],
        CommodityType.FERTILIZER: [ScenarioType.FERTILIZER_FEEDSTOCK_SHOCK.value],
        CommodityType.CRITICAL_MINERALS: [ScenarioType.CRITICAL_MINERAL_EXPORT_RESTRICTION.value],
    }
    return mapping[commodity_type]


def _load_definitions() -> dict[CommodityType, CommodityDefinition]:
    payload = yaml.safe_load(_DATA_FILE.read_text())
    definitions: dict[CommodityType, CommodityDefinition] = {}
    for item in payload.get("commodities", []):
        commodity_type = CommodityType(item["commodity_type"])
        definitions[commodity_type] = CommodityDefinition(
            commodity_type=commodity_type,
            display_name=item["commodity_type"].replace("_", " ").title(),
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


def _roadmap_risk(commodity_type: CommodityType) -> list[RiskScore]:
    return [
        RiskScore(
            entity_id=f"{commodity_type.value}_GLOBAL",
            entity_type=EntityType.DEMAND_SECTOR,
            commodity_type=commodity_type,
            risk_score=42.0,
            risk_level=RiskLevel.MEDIUM,
            previous_score=39.0,
            delta=3.0,
            top_drivers=["Commodity adapter is scaffolded but not yet fed by live ingestion streams."],
            evidence_event_ids=[],
            confidence=0.58,
            assumptions=[],
            audit_id=f"AUD-{commodity_type.value}-ROADMAP",
            updated_at=datetime.now(timezone.utc),
        )
    ]


@router.get("", response_model=list[CommodityDefinition])
def list_commodities() -> list[CommodityDefinition]:
    return list(_load_definitions().values())


@router.get("/{commodity_type}/entities")
def get_commodity_entities(commodity_type: CommodityType) -> dict[str, object]:
    if commodity_type is CommodityType.CRUDE_OIL:
        return {
            "commodity_type": commodity_type,
            "suppliers": [supplier.model_dump() for supplier in _digital_twin.get_suppliers()],
            "routes": [route.model_dump() for route in _digital_twin.get_routes()],
            "refineries": [refinery.model_dump() for refinery in _digital_twin.get_refineries()],
        }
    return {
        "commodity_type": commodity_type,
        "status": "roadmap",
        "scenario_templates": _scenario_templates_for(commodity_type),
        "note": "Schema and templates exist, but commodity-specific entities are not wired to live ingestion yet.",
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
