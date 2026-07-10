"""India import exposure and refinery exposure calculations (Phase 5, section 5.3).

Reads the Phase 2 `DigitalTwinService` in-memory seed data rather than
issuing live Neo4j queries, so exposure figures stay available even
without a running graph database - the same graceful-degradation choice
`agents/entity_resolution_agent.py` made in Phase 4. The underlying numbers
are identical either way since `graph/seed_graph.py` loads the graph from
this same `DigitalTwinService` data.
"""

from __future__ import annotations

from typing import Any

from services.digital_twin_service import DigitalTwinService


def compute_chokepoint_exposure_score(digital_twin: DigitalTwinService, chokepoint_id: str) -> float:
    """0-100: percent of total India crude imports flowing through routes
    that transit this chokepoint (plan section 5.1, step 3: "add exposure
    from graph relationships")."""
    summary = digital_twin.get_exposure_summary()
    return round(min(100.0, summary["chokepoint_exposure_percent"].get(chokepoint_id, 0.0)), 2)


def compute_route_exposure_score(digital_twin: DigitalTwinService, route_id: str) -> float:
    """0-100: percent of total India crude imports assigned to this route
    as a supplier's default shipping route."""
    summary = digital_twin.get_exposure_summary()
    return round(min(100.0, summary["route_exposure_percent"].get(route_id, 0.0)), 2)


def compute_supplier_exposure_score(digital_twin: DigitalTwinService, supplier_id: str) -> float:
    """0-100: this supplier's own import-share percent (plan section 5.2,
    step 4: "add import share exposure")."""
    supplier = digital_twin.find_supplier(supplier_id)
    return round(min(100.0, supplier.import_share_percent), 2) if supplier else 0.0


def get_exposed_refineries(digital_twin: DigitalTwinService, chokepoint_id: str) -> list[dict[str, Any]]:
    """Refineries reachable from routes that transit `chokepoint_id`,
    weighted by each refinery's share of total Indian refining capacity
    (plan section 5.3, step 2: "weight exposure by assumed capacity").

    Mirrors `graph.graph_queries.get_refineries_exposed_to_chokepoint` but
    computed in-memory from Phase 2 data so it works without a live graph.
    """
    exposed_refinery_ids: set[str] = set()
    for route in digital_twin.get_routes():
        if chokepoint_id not in route.affected_chokepoint_ids:
            continue
        import_port = digital_twin.import_ports.get(route.destination_port_id)
        if import_port is None:
            continue
        for refinery in digital_twin.get_refineries():
            if import_port.id in refinery.connected_import_port_ids:
                exposed_refinery_ids.add(refinery.id)

    total_capacity = sum(refinery.capacity_bpd or 0 for refinery in digital_twin.get_refineries())
    if total_capacity <= 0:
        total_capacity = 1

    results = []
    for refinery_id in exposed_refinery_ids:
        refinery = digital_twin.refineries.get(refinery_id)
        if refinery is None:
            continue
        weight = round(((refinery.capacity_bpd or 0) / total_capacity) * 100, 2)
        results.append(
            {
                "refinery_id": refinery.id,
                "name": refinery.name,
                "capacity_weight_percent": weight,
            }
        )
    return sorted(results, key=lambda item: item["capacity_weight_percent"], reverse=True)
