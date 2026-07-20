"""In-memory knowledge graph built from the Phase 2 digital twin.

This is the no-database fallback for every read query in
`graph/graph_queries.py`: it builds exactly the same node labels and
relationship types `graph/seed_graph.py` writes into Neo4j, but from the
in-memory `DigitalTwinService` seed data, so the Knowledge Graph Explorer,
refinery-exposure, alternative-supplier, and impact-traversal features all
work with zero external infrastructure. When a real Neo4j is running,
`graph_queries.py` uses it and this module is never consulted.

Node/edge shapes here match what `graph_queries` returns from Neo4j
record-by-record, so callers (API routes, agents) can't tell which backend
served the result.
"""

from __future__ import annotations

from typing import Any

from services.digital_twin_service import DigitalTwinService


class InMemoryGraph:
    """Adjacency-list view of the digital twin, mirroring seed_graph.py's
    labels and relationship types."""

    def __init__(self, twin: DigitalTwinService):
        self._twin = twin
        # node_id -> {"label": str, "properties": dict}
        self.nodes: dict[str, dict[str, Any]] = {}
        # list of (source_id, rel_type, target_id, properties)
        self.edges: list[tuple[str, str, str, dict[str, Any]]] = []
        self._build()

    # -- construction --------------------------------------------------

    def _add_node(self, label: str, entity_id: str, properties: dict[str, Any]) -> None:
        self.nodes[entity_id] = {"label": label, "properties": {"entity_id": entity_id, **properties}}

    def _add_edge(self, source_id: str, rel_type: str, target_id: str, properties: dict[str, Any] | None = None) -> None:
        # Only create the edge when both endpoints exist, exactly like
        # seed_graph.py's MATCH ... MERGE (which silently no-ops on a
        # missing endpoint).
        if source_id in self.nodes and target_id in self.nodes:
            self.edges.append((source_id, rel_type, target_id, properties or {}))

    def _build(self) -> None:
        twin = self._twin

        for supplier in twin.get_suppliers():
            self._add_node(
                "SupplierCountry",
                supplier.id,
                {
                    "name": supplier.name,
                    "region": getattr(supplier, "region", None),
                    "import_share_percent": getattr(supplier, "import_share_percent", None),
                },
            )
        for port in twin.export_ports.values():
            self._add_node("ExportPort", port.id, {"name": port.name})
        for port in twin.import_ports.values():
            self._add_node("ImportPort", port.id, {"name": port.name})
        for chokepoint in twin.get_chokepoints():
            self._add_node("Chokepoint", chokepoint.id, {"name": chokepoint.name})
        for route in twin.get_routes():
            self._add_node(
                "ShippingRoute",
                route.id,
                {
                    "name": route.name,
                    "estimated_transit_days": getattr(route, "estimated_transit_days", None),
                    "distance_km": getattr(route, "distance_km", None),
                },
            )
        for refinery in twin.get_refineries():
            self._add_node("Refinery", refinery.id, {"name": refinery.name})
        for spr in twin.get_spr_sites():
            self._add_node(
                "StrategicReserveSite",
                spr.id,
                {"name": spr.name, "capacity_mmbbl": getattr(spr, "capacity_mmbbl", None)},
            )

        # Relationships mirror seed_graph.py exactly.
        for supplier in twin.get_suppliers():
            if getattr(supplier, "default_export_port_id", None):
                self._add_edge(supplier.id, "EXPORTS_FROM", supplier.default_export_port_id)

        for route in twin.get_routes():
            self._add_edge(route.origin_port_id, "USES_ROUTE", route.id)
            self._add_edge(route.id, "ARRIVES_AT", route.destination_port_id)
            for chokepoint_id in getattr(route, "affected_chokepoint_ids", []) or []:
                self._add_edge(route.id, "TRANSITS", chokepoint_id)

        for refinery in twin.get_refineries():
            for port_id in getattr(refinery, "connected_import_port_ids", []) or []:
                self._add_edge(port_id, "FEEDS", refinery.id)

        for spr in twin.get_spr_sites():
            for refinery_id in getattr(spr, "supported_refinery_ids", []) or []:
                self._add_edge(spr.id, "CAN_SUPPORT", refinery_id)

    # -- queries (mirror graph_queries.py return shapes) ---------------

    def neighborhood(self, entity_id: str) -> dict[str, Any] | None:
        node = self.nodes.get(entity_id)
        if node is None:
            return None
        edges = []
        for source_id, rel_type, target_id, props in self.edges:
            if source_id == entity_id or target_id == entity_id:
                edges.append(
                    {
                        "source_id": source_id,
                        "target_id": target_id,
                        "relationship_type": rel_type,
                        "properties": props,
                        "confidence": props.get("confidence"),
                    }
                )
        return {
            "nodes": [{"entity_id": entity_id, "label": node["label"], "properties": node["properties"]}],
            "edges": edges,
            "query_description": f"Direct relationships for entity '{entity_id}'",
        }

    def impact_subgraph(self, entity_id: str, max_hops: int) -> dict[str, Any]:
        hops = min(max(int(max_hops), 1), 5)
        if entity_id not in self.nodes:
            return {"nodes": [], "edges": [], "query_description": f"Entity '{entity_id}' not found"}

        # "Downstream impact" is disruption propagation, which runs opposite
        # to some supply-flow edge directions: a blocked Chokepoint impacts
        # the routes that TRANSIT it, then the ImportPorts those routes
        # ARRIVE_AT, then the Refineries those ports FEED. Those three edge
        # types are stored source->target in supply-flow orientation
        # (route->chokepoint, route->port, port->refinery), so we traverse
        # them in reverse; the remaining edge types propagate forward. This
        # yields the Chokepoint -> Route -> Refinery view the Knowledge
        # Graph Explorer shows.
        _REVERSED = {"TRANSITS", "ARRIVES_AT", "FEEDS", "EXPORTS_FROM", "USES_ROUTE"}
        # Each adjacency entry: (neighbor_to_visit, rel_type, props, true_source, true_target)
        # where true_source/true_target preserve the edge's real supply-flow
        # orientation for the emitted diagram, independent of walk direction.
        adjacency: dict[str, list[tuple[str, str, dict[str, Any], str, str]]] = {}
        for source_id, rel_type, target_id, props in self.edges:
            if rel_type in _REVERSED:
                adjacency.setdefault(target_id, []).append((source_id, rel_type, props, source_id, target_id))
            else:
                adjacency.setdefault(source_id, []).append((target_id, rel_type, props, source_id, target_id))

        visited_nodes: dict[str, dict[str, Any]] = {}
        collected_edges: list[dict[str, Any]] = []
        seen_edges: set[tuple[str, str, str]] = set()

        def visit(current: str, depth: int) -> None:
            node = self.nodes.get(current)
            if node and current not in visited_nodes:
                visited_nodes[current] = {"entity_id": current, "label": node["label"], "properties": node["properties"]}
            if depth >= hops:
                return
            for neighbor_id, rel_type, props, true_source, true_target in adjacency.get(current, []):
                edge_key = (true_source, rel_type, true_target)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    collected_edges.append(
                        {
                            "source_id": true_source,
                            "target_id": true_target,
                            "relationship_type": rel_type,
                            "properties": props,
                            "confidence": props.get("confidence"),
                        }
                    )
                neighbor_node = self.nodes.get(neighbor_id)
                if neighbor_node and neighbor_id not in visited_nodes:
                    visited_nodes[neighbor_id] = {
                        "entity_id": neighbor_id,
                        "label": neighbor_node["label"],
                        "properties": neighbor_node["properties"],
                    }
                visit(neighbor_id, depth + 1)

        visit(entity_id, 0)

        if not collected_edges:
            return {
                "nodes": list(visited_nodes.values()),
                "edges": [],
                "query_description": f"No downstream impact found for entity '{entity_id}' within {hops} hop(s)",
            }
        return {
            "nodes": list(visited_nodes.values()),
            "edges": collected_edges,
            "query_description": f"Downstream impact of '{entity_id}' within {hops} hop(s)",
        }

    def refineries_exposed_to_chokepoint(self, chokepoint_id: str) -> list[dict[str, Any]]:
        # Chokepoint <-[:TRANSITS]- ShippingRoute -[:ARRIVES_AT]-> ImportPort -[:FEEDS]-> Refinery
        routes_transiting = [s for (s, rel, t, _p) in self.edges if rel == "TRANSITS" and t == chokepoint_id]
        results: dict[str, dict[str, Any]] = {}
        for route_id in routes_transiting:
            import_ports = [t for (s, rel, t, _p) in self.edges if rel == "ARRIVES_AT" and s == route_id]
            for port_id in import_ports:
                refineries = [t for (s, rel, t, _p) in self.edges if rel == "FEEDS" and s == port_id]
                for refinery_id in refineries:
                    node = self.nodes.get(refinery_id, {})
                    results.setdefault(
                        refinery_id,
                        {
                            "entity_id": refinery_id,
                            "name": node.get("properties", {}).get("name"),
                            "risk_level": node.get("properties", {}).get("risk_level"),
                            "via_route_id": route_id,
                        },
                    )
        return list(results.values())

    def routes_for_supplier(self, supplier_id: str) -> list[dict[str, Any]]:
        export_ports = [t for (s, rel, t, _p) in self.edges if rel == "EXPORTS_FROM" and s == supplier_id]
        results: dict[str, dict[str, Any]] = {}
        for port_id in export_ports:
            route_ids = [t for (s, rel, t, _p) in self.edges if rel == "USES_ROUTE" and s == port_id]
            for route_id in route_ids:
                props = self.nodes.get(route_id, {}).get("properties", {})
                results.setdefault(
                    route_id,
                    {
                        "entity_id": route_id,
                        "name": props.get("name"),
                        "risk_level": props.get("risk_level"),
                        "estimated_transit_days": props.get("estimated_transit_days"),
                        "distance_km": props.get("distance_km"),
                    },
                )
        return list(results.values())

    def entity_name(self, entity_id: str) -> str | None:
        return self.nodes.get(entity_id, {}).get("properties", {}).get("name")


_default_graph: InMemoryGraph | None = None


def get_in_memory_graph() -> InMemoryGraph:
    """Process-wide in-memory graph, built once from the default seed data."""
    global _default_graph
    if _default_graph is None:
        twin = DigitalTwinService()
        twin.load_seed_data()
        _default_graph = InMemoryGraph(twin)
    return _default_graph
