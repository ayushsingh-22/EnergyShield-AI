"""Background risk scoring jobs (Phase 10, section 10.3)."""

from __future__ import annotations

from models.risk_schema import RiskScore
from services.risk_service import RiskService


def run_risk_scoring_job(risk_service: RiskService) -> list[RiskScore]:
    """Recomputes and returns every corridor/supplier risk score from the
    current event set (section 10.3: "update knowledge graph and risk
    scores after event extraction"). `RiskService.refresh()` already
    pushes any changed score into the graph via
    `graph.risk_graph_updater`, so a single call here satisfies both the
    "risk scoring" and "risk graph update" steps."""
    risk_service.refresh()
    return risk_service.get_corridors() + risk_service.get_suppliers()
