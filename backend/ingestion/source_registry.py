"""Central registry of source URLs, refresh intervals, reliability tiers, and fallback modes (Phase 1, section 1.1)."""

from __future__ import annotations

from backend.models.data_source_schema import DataSourceDefinition


def get_active_sources() -> list[DataSourceDefinition]:
    raise NotImplementedError


def get_source_reliability(source_name: str) -> str:
    raise NotImplementedError
