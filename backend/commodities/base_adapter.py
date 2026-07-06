"""Base adapter interface all commodity adapters implement (Phase 14 multi-commodity expansion)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CommodityAdapter(ABC):
    commodity_type: str

    @abstractmethod
    def get_supply_chain_entities(self) -> list[dict[str, Any]]:
        """Return suppliers, routes, ports, processing sites, demand nodes."""
        raise NotImplementedError

    @abstractmethod
    def get_risk_features(self, signals: list[dict[str, Any]]) -> dict[str, float]:
        """Convert normalized signals into commodity-specific risk features."""
        raise NotImplementedError

    @abstractmethod
    def get_scenario_templates(self) -> list[str]:
        """Return scenario template IDs supported by this commodity."""
        raise NotImplementedError

    @abstractmethod
    def get_recommendation_constraints(self) -> dict[str, Any]:
        """Return procurement, storage, transport, quality, and substitution constraints."""
        raise NotImplementedError
