"""Stores and retrieves current and historical risk scores backing the risk API (Phase 5)."""

from __future__ import annotations

import logging
from typing import Optional

from graph.risk_graph_updater import update_risk_scores
from models.core_schema import EntityType
from models.risk_schema import RiskScore
from risk.risk_scoring_engine import RiskScoringEngine
from services.digital_twin_service import DigitalTwinService
from services.event_service import EventService

logger = logging.getLogger(__name__)

_CORRIDOR_ENTITY_TYPES = (EntityType.CHOKEPOINT, EntityType.SHIPPING_ROUTE)

# History only grows on a genuine score change (not on every read), so this
# is a generous cap rather than a tight one - it exists purely so a
# long-running process can't accumulate an unbounded per-entity list over
# weeks/months of real score movements.
_MAX_HISTORY_ENTRIES_PER_ENTITY = 200


class RiskService:
    """Recomputes risk scores from the current live event set on every
    read - cheap, pure in-memory computation, and no Phase 10 scheduler
    exists yet, so "always fresh on read" is simpler and just as correct
    as a background refresh loop. Keeps a change-triggered history per
    entity for trend charts (Phase 5 validation: "risk history is stored
    for trend charts and continuous learning")."""

    def __init__(
        self,
        digital_twin: Optional[DigitalTwinService] = None,
        event_service: Optional[EventService] = None,
        engine: Optional[RiskScoringEngine] = None,
    ) -> None:
        self.digital_twin = digital_twin
        self.event_service = event_service
        self.engine = engine or RiskScoringEngine(digital_twin)
        self._current: dict[str, RiskScore] = {}
        self._history: dict[str, list[RiskScore]] = {}

    def refresh(self) -> None:
        """Recomputes every entity's score from the current event set. A
        score only overwrites `previous_score`/`delta` and gets a new
        history entry when it actually changed value, so calling this
        repeatedly with unchanged input doesn't spam history."""
        events = self.event_service.get_all() if self.event_service is not None else []
        computed = self.engine.score_all(events)

        changed: list[RiskScore] = []
        for score in computed:
            previous = self._current.get(score.entity_id)
            if previous is None or previous.risk_score != score.risk_score:
                score = score.model_copy(
                    update={
                        "previous_score": previous.risk_score if previous else None,
                        "delta": (
                            round(score.risk_score - previous.risk_score, 1) if previous is not None else None
                        ),
                    }
                )
                entity_history = self._history.setdefault(score.entity_id, [])
                entity_history.append(score)
                if len(entity_history) > _MAX_HISTORY_ENTRIES_PER_ENTITY:
                    del entity_history[: len(entity_history) - _MAX_HISTORY_ENTRIES_PER_ENTITY]
                changed.append(score)
                self._current[score.entity_id] = score
            else:
                self._current[score.entity_id] = previous

        if changed:
            try:
                update_risk_scores(changed)
            except Exception:  # noqa: BLE001 - graph push failures must not break the risk API
                logger.exception("Failed to push %d updated risk score(s) into the graph", len(changed))

    def get_corridors(self) -> list[RiskScore]:
        self.refresh()
        return [score for score in self._current.values() if score.entity_type in _CORRIDOR_ENTITY_TYPES]

    def get_suppliers(self) -> list[RiskScore]:
        self.refresh()
        return [score for score in self._current.values() if score.entity_type == EntityType.SUPPLIER_COUNTRY]

    def get_refineries(self) -> list[RiskScore]:
        self.refresh()
        return [score for score in self._current.values() if score.entity_type == EntityType.REFINERY]

    def get_history(self, entity_id: str) -> list[RiskScore]:
        self.refresh()
        return list(self._history.get(entity_id, []))
