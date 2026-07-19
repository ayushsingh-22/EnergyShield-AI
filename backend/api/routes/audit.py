"""Immutable audit trail endpoint (Phase 8 persistence / Phase 11 explainability)."""

from __future__ import annotations

from fastapi import APIRouter

from models.core_schema import AuditEvent
from services.audit_service import AuditService

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])
_audit_service = AuditService()


@router.get("/{entity_id}", response_model=list[AuditEvent])
def get_audit_trail(entity_id: str) -> list[AuditEvent]:
    """Every recorded audit entry for one entity (event/scenario/
    recommendation/report id), oldest first."""
    return _audit_service.get_events_for_entity(entity_id)


def get_audit_service() -> AuditService:
    """Exposes the module-level `AuditService` singleton so other routers
    can record audit events against the same log this endpoint reads from -
    the same pattern `api/routes/events.py::get_event_service` uses."""
    return _audit_service
