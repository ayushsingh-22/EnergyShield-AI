"""Knowledge graph query endpoints (Phase 3 knowledge graph foundation).

See docs/API_REFERENCE.md for the endpoints this router will own.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from graph import graph_queries
from models.graph_schema import GraphQueryResult, ImpactQueryRequest

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


@router.get("/entity/{entity_id}", response_model=GraphQueryResult)
def get_entity(entity_id: str):
    """Node plus its direct relationships."""
    result = graph_queries.get_entity_neighborhood(entity_id)
    if not result["nodes"]:
        raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found in knowledge graph")
    return result


@router.get("/refineries-exposed")
def get_refineries_exposed(chokepoint_id: str = Query(...)):
    """Refineries exposed to a disruption at the given chokepoint."""
    return graph_queries.get_refineries_exposed_to_chokepoint(chokepoint_id)


@router.get("/alternative-suppliers")
def get_alternative_suppliers(supplier_id: str = Query(...), commodity: str = Query(...)):
    """Candidate replacement suppliers for a disrupted supplier."""
    return graph_queries.get_alternative_suppliers(commodity, supplier_id)


@router.get("/routes")
def get_routes(supplier_id: str = Query(...)):
    """Shipping routes a supplier country uses to reach India."""
    return graph_queries.get_routes_for_supplier(supplier_id)


@router.post("/query-impact", response_model=GraphQueryResult)
def query_impact(request: ImpactQueryRequest):
    """Generic downstream-impact traversal from any entity in the graph."""
    return graph_queries.get_impact_subgraph(request.entity_id, request.max_hops)
