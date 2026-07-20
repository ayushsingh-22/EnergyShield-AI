"""Aggregates geopolitical signals and graph exposure into corridor/supplier risk context for the scoring engine."""

from __future__ import annotations

from models.risk_schema import RiskScore
from services.risk_service import RiskService


class GeopoliticalRiskAgent:
    """Agent-layer entry point over `RiskService` (Phase 5's real scoring
    engine): assembles corridors, suppliers, and refineries into one
    consolidated risk briefing and surfaces the entities currently driving
    the most concern, rather than requiring callers to know about the three
    separate `RiskService` getters."""

    def __init__(self, risk_service: RiskService | None = None):
        self._risk_service = risk_service or RiskService()

    def get_risk_briefing(self) -> dict[str, list[RiskScore]]:
        return {
            "corridors": self._risk_service.get_corridors(),
            "suppliers": self._risk_service.get_suppliers(),
            "refineries": self._risk_service.get_refineries(),
        }

    def get_top_concerns(self, limit: int = 5) -> list[RiskScore]:
        """Ranks every scored entity by `risk_score` descending, regardless
        of entity type - the single "what should an analyst look at first"
        view the plan's Phase 5 objectives describe ("generate live risk
        scores... for corridors, suppliers, routes, ports, refineries")."""
        briefing = self.get_risk_briefing()
        all_scores = briefing["corridors"] + briefing["suppliers"] + briefing["refineries"]
        return sorted(all_scores, key=lambda score: score.risk_score, reverse=True)[:limit]
