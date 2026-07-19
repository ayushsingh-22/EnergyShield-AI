"""Stores feature vectors used by risk and scenario models, linked to model version and output score (Phase 13, section 13.2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class FeatureSnapshot:
    entity_id: str
    timestamp: datetime
    model_version: str
    features: dict[str, float]
    output_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class FeatureStore:
    """Append-only feature history (section 13.2, step 3: "preserve
    features for backtesting"). Never mutates a stored snapshot - only
    appends - so a past scenario/risk-score result stays reproducible from
    the exact feature vector that was active when it was generated (the
    continuous-learning governance rule in docs/CONTINUOUS_LEARNING.md)."""

    def __init__(self):
        self._snapshots: list[FeatureSnapshot] = []

    def record(self, snapshot: FeatureSnapshot) -> FeatureSnapshot:
        self._snapshots.append(snapshot)
        return snapshot

    def get_for_entity(self, entity_id: str) -> list[FeatureSnapshot]:
        return [snapshot for snapshot in self._snapshots if snapshot.entity_id == entity_id]

    def get_for_model_version(self, model_version: str) -> list[FeatureSnapshot]:
        return [snapshot for snapshot in self._snapshots if snapshot.model_version == model_version]

    def all(self) -> list[FeatureSnapshot]:
        return list(self._snapshots)


_default_store: FeatureStore | None = None


def get_feature_store() -> FeatureStore:
    """Returns the process-wide `FeatureStore` singleton."""
    global _default_store
    if _default_store is None:
        _default_store = FeatureStore()
    return _default_store
