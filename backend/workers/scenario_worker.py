"""Scenario trigger jobs (Phase 10, section 10.4)."""

from __future__ import annotations

import os

from models.core_schema import CommodityType, RiskLevel
from models.risk_schema import RiskScore
from models.scenario_schema import ScenarioRequest, ScenarioResult, ScenarioType
from services.scenario_service import ScenarioService

# Section 10.4: risk score threshold above which a scenario auto-triggers.
# Kept in sync with SCENARIO_RISK_TRIGGER_THRESHOLD in .env.example.
RISK_TRIGGER_THRESHOLD = float(os.getenv("SCENARIO_RISK_TRIGGER_THRESHOLD", "70"))

# Which scenario template auto-runs when a given corridor/supplier entity's
# risk score crosses the threshold (section 10.4, step 1: "find scenario
# templates linked to the event") - the reverse direction of the
# resolution `scenarios/scenario_engine.py` performs from scenario type to
# entity ids.
_ENTITY_SCENARIO_TRIGGERS: dict[str, ScenarioType] = {
    "CHK_HORMUZ": ScenarioType.HORMUZ_PARTIAL_CLOSURE,
    "CHK_BAB": ScenarioType.RED_SEA_SHIPPING_DISRUPTION,
    "CHK_SUEZ": ScenarioType.RED_SEA_SHIPPING_DISRUPTION,
    "SUP_RUS": ScenarioType.SANCTIONS_SHOCK,
}


def find_triggered_scenario_requests(
    scores: list[RiskScore], threshold: float = RISK_TRIGGER_THRESHOLD
) -> list[ScenarioRequest]:
    """Section 10.4, step 1: "if corridor risk > threshold, find scenario
    templates linked to the event"."""
    requests = []
    for score in scores:
        if score.risk_score < threshold:
            continue
        scenario_type = _ENTITY_SCENARIO_TRIGGERS.get(score.entity_id)
        if scenario_type is None:
            continue
        severity = RiskLevel.CRITICAL if score.risk_score >= 90 else RiskLevel.SEVERE
        requests.append(
            ScenarioRequest(
                scenario_type=scenario_type,
                commodity_type=CommodityType.CRUDE_OIL,
                duration_days=15,
                severity=severity,
                affected_entities=[score.entity_id],
            )
        )
    return requests


def run_scenario_trigger_job(scores: list[RiskScore], scenario_service: ScenarioService) -> list[ScenarioResult]:
    """Section 10.4, steps 2-3: "run scenario in background" (the caller -
    `orchestration.workflows` - handles "notify dashboard" by publishing
    each result to the event bus)."""
    requests = find_triggered_scenario_requests(scores)
    return [scenario_service.run_scenario(request) for request in requests]
