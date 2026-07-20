"""Corridor and supplier risk card and history endpoints (Phase 5 risk scoring engine)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.routes.events import get_event_service
from models.risk_schema import RiskScore
from services.risk_service import RiskService

router = APIRouter(prefix="/api/v1/risk", tags=["risk"])
# Wires the live Phase 4 event feed into the Phase 5 scoring engine so
# corridor/supplier scores reflect real extracted events instead of static
# demo data (plan Phase 5 validation: "risk score changes when a
# high-severity event is added").
_service = RiskService(event_service=get_event_service())


@router.get("/corridors", response_model=list[RiskScore])
def get_corridor_risk() -> list[RiskScore]:
    return _service.get_corridors()


@router.get("/suppliers", response_model=list[RiskScore])
def get_supplier_risk() -> list[RiskScore]:
    return _service.get_suppliers()


@router.get("/history/{entity_id}", response_model=list[RiskScore])
def get_risk_history(entity_id: str) -> list[RiskScore]:
    history = _service.get_history(entity_id)
    if not history:
        raise HTTPException(status_code=404, detail=f"No risk history found for '{entity_id}'")
    return history


def get_risk_service() -> RiskService:
    """Exposes the module-level `RiskService` singleton so Phase 10's
    orchestration workers can recompute/read the same scores this router
    serves, same pattern as `api/routes/events.py::get_event_service`."""
    return _service
