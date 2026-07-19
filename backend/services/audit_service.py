"""Immutable audit event recording and retrieval, backing GET /api/v1/audit/{entity_id} (Phase 8 / Phase 11)."""

from __future__ import annotations

from datetime import datetime, timezone
from itertools import count
from typing import Any

from models.core_schema import AuditEvent
from storage import repository

# Per-process monotonic counter so audit ids stay unique and ordered within
# a single run, independent of wall-clock resolution.
_counter = count(1)


class AuditService:
    """Records one immutable entry per event/scenario/recommendation/report
    the platform produces (Planning Principle: every output must be
    explainable and traceable) and answers `GET /api/v1/audit/{entity_id}`.

    Reads always come from this process's own in-memory log - the
    authoritative, always-available source - while every write is also
    mirrored to Postgres (best-effort, via `storage.repository`) for
    durability across restarts once a database is actually running.
    """

    def __init__(self) -> None:
        self._events: dict[str, list[AuditEvent]] = {}

    def record_event(
        self,
        *,
        entity_id: str,
        entity_type: str,
        action: str,
        summary: str,
        actor: str = "system",
        source_event_ids: list[str] | None = None,
        model_version: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            audit_id=f"AUD-{next(_counter):06d}",
            entity_id=entity_id,
            entity_type=entity_type,
            action=action,
            actor=actor,
            timestamp=datetime.now(timezone.utc),
            source_event_ids=source_event_ids or [],
            model_version=model_version,
            summary=summary,
            details=details or {},
        )
        self._events.setdefault(entity_id, []).append(event)
        repository.save_audit_event(event.audit_id, entity_id, event.model_dump_json())
        return event

    def get_events_for_entity(self, entity_id: str) -> list[AuditEvent]:
        return list(self._events.get(entity_id, []))
