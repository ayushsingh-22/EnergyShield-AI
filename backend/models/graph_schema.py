"""Generic Pydantic schemas for graph nodes, edges, and query results (Phase 3 knowledge graph foundation)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from models.core_schema import EnergyShieldBaseModel


class GraphNode(EnergyShieldBaseModel):
    """A single node returned from a knowledge graph query."""

    entity_id: str
    label: str = Field(..., description="Node label, e.g. Refinery, Chokepoint, RiskEvent.")
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(EnergyShieldBaseModel):
    """A single relationship returned from a knowledge graph query."""

    source_id: str
    target_id: str
    relationship_type: str = Field(..., description="e.g. AFFECTS, FEEDS, USES_ROUTE.")
    properties: dict[str, Any] = Field(default_factory=dict)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime | None = None


class GraphQueryResult(EnergyShieldBaseModel):
    """Generic response shape for graph API endpoints (entity lookups, impact queries)."""

    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    query_description: str | None = None


class ImpactQueryRequest(EnergyShieldBaseModel):
    """Body for POST /api/v1/graph/query-impact.

    Traverses outward from `entity_id` along the graph's forward
    relationships (e.g. Chokepoint -> ShippingRoute -> ImportPort ->
    Refinery) to surface everything that could be downstream-impacted.
    """

    entity_id: str
    max_hops: int = Field(default=2, ge=1, le=5)
