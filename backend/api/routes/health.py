"""GET /api/v1/health - liveness check used by docker-compose and the demo."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from backend.models.core_schema import EnergyShieldBaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus(EnergyShieldBaseModel):
    status: str
    service: str
    version: str
    checked_at: datetime


@router.get("", response_model=HealthStatus)
def get_health() -> HealthStatus:
    return HealthStatus(
        status="ok",
        service="energyshield-backend",
        version="0.1.0",
        checked_at=datetime.now(timezone.utc),
    )
