"""Risk event persistence and retrieval logic backing the events API (Phase 4).

Stores extracted events in memory, keyed by `event_id`, mirroring the
in-memory-dict pattern `services/digital_twin_service.py` already uses for
seed data - there is no database session wired up yet (Phase 8).
"""

from __future__ import annotations

from typing import Dict, List, Optional

from models.event_schema import RiskEvent


class EventService:
    def __init__(self):
        self._events: Dict[str, RiskEvent] = {}

    def add_event(self, event: RiskEvent) -> RiskEvent:
        self._events[event.event_id] = event
        return event

    def add_events(self, events: List[RiskEvent]) -> List[RiskEvent]:
        return [self.add_event(event) for event in events]

    def replace_all(self, events: List[RiskEvent]) -> List[RiskEvent]:
        """Replaces the entire store with `events` in one atomic swap.

        Used by a pipeline run that re-fetches the current state of the
        world (e.g. `api/routes/events.py::run_extraction_pipeline`) rather
        than appending to history - re-running it must not accumulate
        duplicate events forever."""
        self._events = {}
        return self.add_events(events)

    def get_event(self, event_id: str) -> Optional[RiskEvent]:
        return self._events.get(event_id)

    def get_latest(self, limit: int = 50) -> List[RiskEvent]:
        events = sorted(self._events.values(), key=lambda event: event.detected_at, reverse=True)
        return events[:limit]

    def get_all(self) -> List[RiskEvent]:
        return list(self._events.values())

    def count(self) -> int:
        return len(self._events)
