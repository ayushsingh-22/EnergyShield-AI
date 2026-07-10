"""Scenario run persistence and retrieval backing the scenarios API (Phase 6)."""

from __future__ import annotations

from datetime import datetime, timezone
from itertools import count

from models.core_schema import Assumption, RiskLevel
from models.scenario_schema import AffectedRefinery, ScenarioRequest, ScenarioResult, ScenarioType
from services.digital_twin_service import DigitalTwinService

_TEMPLATE_FACTORS: dict[ScenarioType, dict[str, float | bool]] = {
    ScenarioType.HORMUZ_PARTIAL_CLOSURE: {
        "supply_at_risk_percent": 31.0,
        "estimated_delay_days": 9.0,
        "freight_cost_impact_percent": 18.0,
        "action_required": True,
    },
    ScenarioType.RED_SEA_SHIPPING_DISRUPTION: {
        "supply_at_risk_percent": 22.0,
        "estimated_delay_days": 12.0,
        "freight_cost_impact_percent": 15.0,
        "action_required": True,
    },
    ScenarioType.OPEC_SUPPLY_CUT: {
        "supply_at_risk_percent": 14.0,
        "estimated_delay_days": 4.0,
        "freight_cost_impact_percent": 9.0,
        "action_required": True,
    },
    ScenarioType.SANCTIONS_SHOCK: {
        "supply_at_risk_percent": 17.0,
        "estimated_delay_days": 6.0,
        "freight_cost_impact_percent": 11.0,
        "action_required": True,
    },
    ScenarioType.PORT_CONGESTION: {
        "supply_at_risk_percent": 10.0,
        "estimated_delay_days": 7.0,
        "freight_cost_impact_percent": 6.0,
        "action_required": False,
    },
    ScenarioType.LNG_SUPPLY_SHOCK: {
        "supply_at_risk_percent": 18.0,
        "estimated_delay_days": 8.0,
        "freight_cost_impact_percent": 13.0,
        "action_required": True,
    },
    ScenarioType.COAL_IMPORT_DISRUPTION: {
        "supply_at_risk_percent": 16.0,
        "estimated_delay_days": 10.0,
        "freight_cost_impact_percent": 8.0,
        "action_required": True,
    },
    ScenarioType.FERTILIZER_FEEDSTOCK_SHOCK: {
        "supply_at_risk_percent": 12.0,
        "estimated_delay_days": 5.0,
        "freight_cost_impact_percent": 14.0,
        "action_required": True,
    },
    ScenarioType.CRITICAL_MINERAL_EXPORT_RESTRICTION: {
        "supply_at_risk_percent": 9.0,
        "estimated_delay_days": 16.0,
        "freight_cost_impact_percent": 12.0,
        "action_required": True,
    },
}


class ScenarioService:
    def __init__(self) -> None:
        self._results: dict[str, ScenarioResult] = {}
        self._counter = count(1)
        self._digital_twin = DigitalTwinService()
        self._digital_twin.load_seed_data()

    def run_scenario(self, request: ScenarioRequest) -> ScenarioResult:
        profile = _TEMPLATE_FACTORS[request.scenario_type]
        multiplier = {
            RiskLevel.LOW: 0.8,
            RiskLevel.MEDIUM: 1.0,
            RiskLevel.HIGH: 1.2,
            RiskLevel.SEVERE: 1.4,
            RiskLevel.CRITICAL: 1.6,
        }[request.severity]
        created_at = datetime.now(timezone.utc)
        scenario_id = f"SCN-{created_at:%Y%m%d}-{next(self._counter):04d}"
        refineries = self._build_affected_refineries(request)
        result = ScenarioResult(
            scenario_id=scenario_id,
            scenario_type=request.scenario_type,
            commodity_type=request.commodity_type,
            duration_days=request.duration_days,
            supply_at_risk_percent=min(100.0, round(float(profile["supply_at_risk_percent"]) * multiplier, 1)),
            estimated_delay_days=round(float(profile["estimated_delay_days"]) * multiplier, 1),
            freight_cost_impact_percent=round(float(profile["freight_cost_impact_percent"]) * multiplier, 1),
            affected_refineries=refineries,
            recommended_action_required=bool(profile["action_required"] or request.severity in {RiskLevel.SEVERE, RiskLevel.CRITICAL}),
            confidence=round(max(0.55, 0.86 - ((multiplier - 1.0) * 0.1)), 2),
            assumptions=[
                Assumption(description="Scenario outputs are deterministic demo simulations, not calibrated forecasts.", is_simulated=True),
                Assumption(description="Affected refinery list is inferred from seeded route and chokepoint exposure.", is_simulated=True),
            ],
            created_at=created_at,
        )
        self._results[result.scenario_id] = result
        return result

    def get_scenario(self, scenario_id: str) -> ScenarioResult | None:
        return self._results.get(scenario_id)

    def list_supported_scenarios(self) -> list[str]:
        return [scenario_type.value for scenario_type in ScenarioType]

    def _build_affected_refineries(self, request: ScenarioRequest) -> list[AffectedRefinery]:
        refineries = self._digital_twin.get_refineries()
        if not refineries:
            return []

        impacted = refineries[:2] if request.scenario_type in {
            ScenarioType.HORMUZ_PARTIAL_CLOSURE,
            ScenarioType.RED_SEA_SHIPPING_DISRUPTION,
            ScenarioType.SANCTIONS_SHOCK,
        } else refineries[:1]

        exposure = RiskLevel.HIGH if request.severity in {RiskLevel.HIGH, RiskLevel.SEVERE, RiskLevel.CRITICAL} else RiskLevel.MEDIUM
        return [
            AffectedRefinery(
                refinery_id=ref.id,
                exposure_level=exposure,
                reason=f"Seeded dependency graph marks {ref.name} as exposed to the simulated corridor stress.",
            )
            for ref in impacted
        ]
