"""Pydantic schemas for historical cases, model versions, and feedback (Phase 13 continuous learning)."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import Field

from backend.models.core_schema import CommodityType, EnergyShieldBaseModel, RiskEventType


class ObservedOutcome(EnergyShieldBaseModel):
    """Observed real-world outcome of a historical disruption case."""

    average_delay_days: float | None = Field(default=None, ge=0)
    freight_cost_increase_percent: float | None = None
    route_shift_detected: bool | None = None
    price_movement_percent: float | None = None


class HistoricalCase(EnergyShieldBaseModel):
    """Matches the "Historical Case Schema" in Phase 13 of the implementation plan."""

    case_id: str
    case_name: str
    commodity_type: CommodityType
    start_date: date
    end_date: date | None = None
    trigger_events: list[RiskEventType] = Field(default_factory=list)
    affected_corridors: list[str] = Field(default_factory=list)
    observed_outcomes: ObservedOutcome
    source_notes: str | None = None
    is_simulated: bool = True


class ModelVersionStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class ModelVersion(EnergyShieldBaseModel):
    """Tracks a trained/calibrated model or rule-set version for audit replay."""

    model_id: str
    model_name: str
    version: str
    status: ModelVersionStatus = ModelVersionStatus.CANDIDATE
    trained_at: datetime
    training_data_range: str | None = None
    metrics: dict[str, float] = Field(default_factory=dict)
    owner: str | None = None


class FeedbackAction(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


class FeedbackEntry(EnergyShieldBaseModel):
    """Analyst feedback captured against a recommendation (Phase 13, section 13.6)."""

    feedback_id: str
    recommendation_id: str
    useful: bool
    action_taken: FeedbackAction
    rejection_reason: str | None = None
    submitted_by: str | None = None
    submitted_at: datetime
