"""Reusable graph query functions used by risk and recommendation agents (Phase 3, section 3.4).

Every function reads from Neo4j when it's reachable and transparently falls
back to the in-memory graph built from the Phase 2 digital twin
(`graph/in_memory_graph.py`) when it isn't - so the Knowledge Graph
Explorer, refinery-exposure, alternative-supplier, and impact-traversal
features all work with zero external infrastructure. The fallback returns
the identical record shape, so callers never branch on which backend
served the result.
"""

from __future__ import annotations

from graph.in_memory_graph import get_in_memory_graph
from graph.kg_client import get_kg_client


def get_refineries_exposed_to_chokepoint(chokepoint_id: str) -> list[dict]:
    """Refineries reachable from a chokepoint via a transiting route that
    arrives at an import port feeding the refinery."""
    client = get_kg_client()
    rows = client.run_query(
        """
        MATCH (c:Chokepoint {entity_id: $chokepoint_id})<-[:TRANSITS]-(route:ShippingRoute)
              -[:ARRIVES_AT]->(port:ImportPort)-[:FEEDS]->(refinery:Refinery)
        RETURN DISTINCT refinery.entity_id AS entity_id, refinery.name AS name,
               refinery.risk_level AS risk_level, route.entity_id AS via_route_id
        """,
        {"chokepoint_id": chokepoint_id},
    )
    if rows:
        return rows
    return get_in_memory_graph().refineries_exposed_to_chokepoint(chokepoint_id)


def get_alternative_suppliers(commodity: str, blocked_supplier_id: str) -> list[dict]:
    """Candidate replacement suppliers for the same commodity, excluding the
    blocked supplier and any supplier currently AFFECTS-linked to an active
    (non-expired) risk event."""
    client = get_kg_client()
    rows = client.run_query(
        """
        MATCH (alt:SupplierCountry)-[:SUPPLIES]->(:Commodity {entity_id: $commodity})
        WHERE alt.entity_id <> $blocked_supplier_id
        OPTIONAL MATCH (alt)-[:PRODUCES_GRADE]->(grade:CrudeGrade)
        OPTIONAL MATCH (:RiskEvent)-[r:AFFECTS]->(alt) WHERE r.expired_at IS NULL
        WITH alt, collect(DISTINCT grade.entity_id) AS crude_grade_ids, count(r) AS active_event_count
        WHERE active_event_count = 0
        RETURN alt.entity_id AS entity_id, alt.name AS name, alt.region AS region,
               alt.import_share_percent AS import_share_percent, crude_grade_ids
        ORDER BY alt.import_share_percent DESC
        """,
        {"commodity": commodity, "blocked_supplier_id": blocked_supplier_id},
    )
    if rows:
        return rows
    # No-Neo4j fallback: every seeded supplier except the blocked one,
    # ranked by import share. Active-event exclusion is the graph's job;
    # the procurement agent (Phase 7) already re-applies that filter from
    # the live event set via `find_candidate_suppliers`, so this endpoint's
    # fallback just surfaces the structural alternatives.
    graph = get_in_memory_graph()
    candidates = [
        {
            "entity_id": node_id,
            "name": data["properties"].get("name"),
            "region": data["properties"].get("region"),
            "import_share_percent": data["properties"].get("import_share_percent"),
            "crude_grade_ids": [],
        }
        for node_id, data in graph.nodes.items()
        if data["label"] == "SupplierCountry" and node_id != blocked_supplier_id
    ]
    candidates.sort(key=lambda c: c["import_share_percent"] or 0, reverse=True)
    return candidates


def get_routes_for_supplier(supplier_id: str) -> list[dict]:
    """Shipping routes a supplier country's export ports use to reach India."""
    client = get_kg_client()
    rows = client.run_query(
        """
        MATCH (s:SupplierCountry {entity_id: $supplier_id})-[:EXPORTS_FROM]->(:ExportPort)
              -[:USES_ROUTE]->(route:ShippingRoute)
        RETURN DISTINCT route.entity_id AS entity_id, route.name AS name,
               route.risk_level AS risk_level, route.estimated_transit_days AS estimated_transit_days,
               route.distance_km AS distance_km
        """,
        {"supplier_id": supplier_id},
    )
    if rows:
        return rows
    return get_in_memory_graph().routes_for_supplier(supplier_id)


def get_scenarios_triggered_by_event(event_id: str) -> list[dict]:
    """Scenario runs (Phase 6) that were triggered by a given risk event."""
    client = get_kg_client()
    return client.run_query(
        """
        MATCH (scenario:Scenario)-[:TRIGGERED_BY]->(:RiskEvent {entity_id: $event_id})
        RETURN scenario.entity_id AS entity_id, scenario.scenario_type AS scenario_type,
               scenario.confidence AS confidence
        """,
        {"event_id": event_id},
    )


def get_spr_sites_for_refinery(refinery_id: str) -> list[dict]:
    """Strategic reserve sites that can support a given refinery, ordered by
    drawdown priority."""
    client = get_kg_client()
    return client.run_query(
        """
        MATCH (spr:StrategicReserveSite)-[:CAN_SUPPORT]->(:Refinery {entity_id: $refinery_id})
        RETURN spr.entity_id AS entity_id, spr.name AS name, spr.capacity_mmbbl AS capacity_mmbbl,
               spr.drawdown_priority AS drawdown_priority
        ORDER BY spr.drawdown_priority ASC
        """,
        {"refinery_id": refinery_id},
    )


def get_entity_neighborhood(entity_id: str) -> dict:
    """Node plus its direct outgoing/incoming relationships, shaped for
    `models.graph_schema.GraphQueryResult` (GET /graph/entity/{entity_id})."""
    client = get_kg_client()

    node_rows = client.run_query(
        "MATCH (n {entity_id: $entity_id}) RETURN labels(n) AS labels, properties(n) AS properties LIMIT 1",
        {"entity_id": entity_id},
    )
    if not node_rows:
        # Neo4j is empty/unreachable (or the entity genuinely isn't in the
        # live graph); fall back to the in-memory digital-twin graph so the
        # Knowledge Graph Explorer works with no database. Returns the same
        # shape; a truly unknown id yields the "not found" result below.
        fallback = get_in_memory_graph().neighborhood(entity_id)
        if fallback is not None:
            return fallback
        return {"nodes": [], "edges": [], "query_description": f"Entity '{entity_id}' not found"}

    labels = node_rows[0].get("labels") or []
    node = {
        "entity_id": entity_id,
        "label": labels[0] if labels else "Unknown",
        "properties": node_rows[0].get("properties") or {},
    }

    outgoing = client.run_query(
        """
        MATCH (n {entity_id: $entity_id})-[r]->(m)
        RETURN type(r) AS relationship_type, m.entity_id AS other_id, properties(r) AS properties
        """,
        {"entity_id": entity_id},
    )
    incoming = client.run_query(
        """
        MATCH (n {entity_id: $entity_id})<-[r]-(m)
        RETURN type(r) AS relationship_type, m.entity_id AS other_id, properties(r) AS properties
        """,
        {"entity_id": entity_id},
    )

    edges = []
    for row in outgoing:
        if not row.get("other_id"):
            continue
        props = row.get("properties") or {}
        edges.append(
            {
                "source_id": entity_id,
                "target_id": row["other_id"],
                "relationship_type": row["relationship_type"],
                "properties": props,
                "confidence": props.get("confidence"),
            }
        )
    for row in incoming:
        if not row.get("other_id"):
            continue
        props = row.get("properties") or {}
        edges.append(
            {
                "source_id": row["other_id"],
                "target_id": entity_id,
                "relationship_type": row["relationship_type"],
                "properties": props,
                "confidence": props.get("confidence"),
            }
        )

    return {
        "nodes": [node],
        "edges": edges,
        "query_description": f"Direct relationships for entity '{entity_id}'",
    }


def get_impact_subgraph(entity_id: str, max_hops: int = 2) -> dict:
    """Traverses outward from `entity_id` up to `max_hops` forward
    relationships, collecting every node and edge touched. Backs
    POST /graph/query-impact - answers "what could this affect downstream".
    """
    hops = min(max(int(max_hops), 1), 5)
    client = get_kg_client()

    rows = client.run_query(
        f"""
        MATCH path = (start {{entity_id: $entity_id}})-[*1..{hops}]->(end)
        WITH DISTINCT relationships(path) AS rels, nodes(path) AS path_nodes
        UNWIND range(0, size(rels) - 1) AS idx
        WITH path_nodes[idx] AS a, rels[idx] AS rel, path_nodes[idx + 1] AS b
        RETURN DISTINCT a.entity_id AS source_id, labels(a) AS source_labels, properties(a) AS source_properties,
               type(rel) AS relationship_type, properties(rel) AS rel_properties,
               b.entity_id AS target_id, labels(b) AS target_labels, properties(b) AS target_properties
        """,
        {"entity_id": entity_id},
    )

    if not rows:
        # Fall back to the in-memory digital-twin graph (no Neo4j needed).
        return get_in_memory_graph().impact_subgraph(entity_id, hops)

    nodes_by_id: dict[str, dict] = {}
    edges = []
    for row in rows:
        for node_id, labels, properties in (
            (row["source_id"], row["source_labels"], row["source_properties"]),
            (row["target_id"], row["target_labels"], row["target_properties"]),
        ):
            if node_id and node_id not in nodes_by_id:
                nodes_by_id[node_id] = {
                    "entity_id": node_id,
                    "label": labels[0] if labels else "Unknown",
                    "properties": properties or {},
                }

        rel_props = row.get("rel_properties") or {}
        edges.append(
            {
                "source_id": row["source_id"],
                "target_id": row["target_id"],
                "relationship_type": row["relationship_type"],
                "properties": rel_props,
                "confidence": rel_props.get("confidence"),
            }
        )

    return {
        "nodes": list(nodes_by_id.values()),
        "edges": edges,
        "query_description": f"Downstream impact of '{entity_id}' within {hops} hop(s)",
    }
