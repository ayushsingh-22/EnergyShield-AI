"""Scenario run persistence and retrieval backing the scenarios API (Phase 6)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from itertools import count

from models.scenario_schema import ScenarioRequest, ScenarioResult
from reports.formatting import humanize
from scenarios.scenario_engine import ScenarioEngine
from services.audit_service import AuditService
from storage import repository

logger = logging.getLogger(__name__)


class ScenarioService:
    def __init__(self, engine: ScenarioEngine | None = None, audit_service: AuditService | None = None) -> None:
        self._results: dict[str, ScenarioResult] = {}
        self._counter = count(1)
        self._engine = engine or ScenarioEngine()
        self._audit_service = audit_service

    def run_scenario(self, request: ScenarioRequest) -> ScenarioResult:
        created_at = datetime.now(timezone.utc)
        scenario_id = f"SCN-{created_at:%Y%m%d}-{next(self._counter):04d}"
        result = self._engine.run(request, scenario_id=scenario_id, created_at=created_at)
        self._results[result.scenario_id] = result
        repository.save_scenario_run(result.scenario_id, result.model_dump_json())
        if self._audit_service is not None:
            self._audit_service.record_event(
                entity_id=result.scenario_id,
                entity_type="SCENARIO",
                action="SCENARIO_RUN",
                summary=(
                    f"Ran {humanize(result.scenario_type)} scenario "
                    f"({result.supply_at_risk_percent}% supply at risk)."
                ),
                details={"confidence": result.confidence},
            )
        return result

    def get_scenario(self, scenario_id: str) -> ScenarioResult | None:
        """In-memory lookup first (fast path within this process); falls
        back to the Postgres-backed `repository.get_scenario_run` so a
        scenario run survives a process restart when a database is
        actually available. Degrades to the in-memory-only behavior this
        always had when Postgres is unreachable - the payload write in
        `run_scenario` was otherwise dead weight nothing ever read back."""
        cached = self._results.get(scenario_id)
        if cached is not None:
            return cached

        rows = repository.get_scenario_run(scenario_id)
        if not rows:
            return None
        try:
            result = ScenarioResult.model_validate_json(rows[-1]["payload"])
        except Exception:  # noqa: BLE001 - a corrupt/stale row must not break retrieval
            logger.exception("Failed to deserialize stored scenario run '%s'", scenario_id)
            return None
        self._results[scenario_id] = result
        return result

    def list_supported_scenarios(self) -> list[str]:
        return self._engine.list_supported_scenarios()
