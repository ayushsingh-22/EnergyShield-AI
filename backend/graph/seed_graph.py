"""Loads digital twin seed data (CSV/GeoJSON) into Neo4j and creates baseline relationships.

Consumes `services.digital_twin_service.DigitalTwinService` directly (Phase 2
is the canonical source of truth for these entities - see Phase 2 "Future
Integration" note in ENERGYSHIELD_IMPLEMENTATION_PLAN.md) rather than
re-reading the seed CSV/GeoJSON files itself.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from graph.kg_client import KGClient, get_kg_client
from services.digital_twin_service import DigitalTwinService

logger = logging.getLogger(__name__)

_COMMODITY_DEFINITIONS_FILE = "commodity_definitions.yaml"

# Same anchoring as services.digital_twin_service._DEFAULT_DATA_DIR - this
# file also lives two directories below the repo/app root (backend/graph/).
_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "seeds"


def _flatten_properties(data: dict[str, Any]) -> dict[str, Any]:
    """Drops fields Neo4j can't store as a node/relationship property
    (nested dicts, GeoJSON geometry) and stringifies datetimes."""
    flat: dict[str, Any] = {}
    for key, value in data.items():
        if key == "coordinates" or value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            flat[key] = value
        elif isinstance(value, list) and all(isinstance(v, (str, int, float, bool)) for v in value):
            flat[key] = value
        elif isinstance(value, datetime):
            flat[key] = value.isoformat()
    return flat


def _entity_properties(entity: Any) -> dict[str, Any]:
    data = entity.model_dump(by_alias=True)
    props = _flatten_properties(data)
    coordinates = data.get("coordinates")
    if coordinates:
        props["latitude"] = coordinates.get("latitude")
        props["longitude"] = coordinates.get("longitude")
    return props


def _merge_node(client: KGClient, label: str, entity_id: str, properties: dict[str, Any]) -> None:
    client.run_query(
        f"MERGE (n:{label} {{entity_id: $entity_id}}) SET n += $properties",
        {"entity_id": entity_id, "properties": properties},
    )


def _merge_relationship(
    client: KGClient,
    from_label: str,
    from_id: str,
    rel_type: str,
    to_label: str,
    to_id: str,
    properties: dict[str, Any] | None = None,
) -> bool:
    """Returns True if both endpoints existed and the edge was merged."""
    result = client.run_query(
        f"MATCH (a:{from_label} {{entity_id: $from_id}}), (b:{to_label} {{entity_id: $to_id}}) "
        f"MERGE (a)-[r:{rel_type}]->(b) SET r += $properties "
        "RETURN a.entity_id AS matched",
        {"from_id": from_id, "to_id": to_id, "properties": properties or {}},
    )
    return len(result) > 0


def _load_commodity_nodes(client: KGClient, data_dir: str) -> list[str]:
    """Loads Commodity nodes from commodity_definitions.yaml. Returns the
    list of commodity_type ids created (used for SUPPLIES edges)."""
    file_path = Path(data_dir) / _COMMODITY_DEFINITIONS_FILE
    if not file_path.exists():
        logger.warning("Commodity definitions not found at %s; skipping Commodity nodes", file_path)
        return []

    with open(file_path, "r") as f:
        data = yaml.safe_load(f) or {}

    commodity_ids = []
    for commodity in data.get("commodities", []):
        commodity_type = commodity.get("commodity_type")
        if not commodity_type:
            continue
        _merge_node(
            client,
            "Commodity",
            commodity_type,
            {
                "entity_id": commodity_type,
                "commodity_type": commodity_type,
                "status": commodity.get("status", "roadmap"),
            },
        )
        commodity_ids.append(commodity_type)
    return commodity_ids


def load_seed_graph(client: KGClient | None = None, data_dir: str | Path = _DEFAULT_DATA_DIR) -> dict[str, int]:
    """Loads Digital Twin entities and baseline relationships into Neo4j.

    Idempotent: every write uses MERGE, so re-running against an
    already-seeded graph updates properties instead of duplicating nodes
    or edges.
    """
    client = client or get_kg_client()

    twin = DigitalTwinService(data_dir=data_dir)
    twin.load_seed_data()

    counts = {"nodes": 0, "relationships": 0, "validation_warnings": 0}

    commodity_ids = _load_commodity_nodes(client, data_dir)
    counts["nodes"] += len(commodity_ids)

    known_port_ids = set(twin.export_ports.keys()) | set(twin.import_ports.keys())

    for supplier in twin.get_suppliers():
        _merge_node(client, "SupplierCountry", supplier.id, _entity_properties(supplier))
        counts["nodes"] += 1

        if supplier.default_export_port_id:
            if _merge_relationship(
                client, "SupplierCountry", supplier.id, "EXPORTS_FROM", "ExportPort", supplier.default_export_port_id
            ):
                counts["relationships"] += 1
            else:
                logger.warning(
                    "Supplier %s references unknown export port %s", supplier.id, supplier.default_export_port_id
                )
                counts["validation_warnings"] += 1

        for commodity_type in supplier.commodity_support:
            if commodity_type in commodity_ids and _merge_relationship(
                client, "SupplierCountry", supplier.id, "SUPPLIES", "Commodity", commodity_type
            ):
                counts["relationships"] += 1

        for grade_id in supplier.supported_crude_grade_ids:
            if _merge_relationship(client, "SupplierCountry", supplier.id, "PRODUCES_GRADE", "CrudeGrade", grade_id):
                counts["relationships"] += 1

    for port in twin.export_ports.values():
        _merge_node(client, "ExportPort", port.id, _entity_properties(port))
        counts["nodes"] += 1

    for port in twin.import_ports.values():
        _merge_node(client, "ImportPort", port.id, _entity_properties(port))
        counts["nodes"] += 1

    for chokepoint in twin.get_chokepoints():
        _merge_node(client, "Chokepoint", chokepoint.id, _entity_properties(chokepoint))
        counts["nodes"] += 1

    for route in twin.get_routes():
        _merge_node(client, "ShippingRoute", route.id, _entity_properties(route))
        counts["nodes"] += 1

        if route.origin_port_id not in known_port_ids or route.destination_port_id not in known_port_ids:
            logger.warning(
                "Route %s does not connect two known ports (origin=%s, destination=%s)",
                route.id,
                route.origin_port_id,
                route.destination_port_id,
            )
            counts["validation_warnings"] += 1

        if _merge_relationship(
            client, "ExportPort", route.origin_port_id, "USES_ROUTE", "ShippingRoute", route.id
        ):
            counts["relationships"] += 1
        if _merge_relationship(
            client, "ShippingRoute", route.id, "ARRIVES_AT", "ImportPort", route.destination_port_id
        ):
            counts["relationships"] += 1
        for chokepoint_id in route.affected_chokepoint_ids:
            if _merge_relationship(client, "ShippingRoute", route.id, "TRANSITS", "Chokepoint", chokepoint_id):
                counts["relationships"] += 1

    for refinery in twin.get_refineries():
        _merge_node(client, "Refinery", refinery.id, _entity_properties(refinery))
        counts["nodes"] += 1

        for port_id in refinery.connected_import_port_ids:
            if _merge_relationship(client, "ImportPort", port_id, "FEEDS", "Refinery", refinery.id):
                counts["relationships"] += 1
            else:
                logger.warning("Refinery %s references unknown import port %s", refinery.id, port_id)
                counts["validation_warnings"] += 1

        for grade_id in refinery.accepted_crude_grade_ids:
            if _merge_relationship(client, "Refinery", refinery.id, "ACCEPTS_GRADE", "CrudeGrade", grade_id):
                counts["relationships"] += 1

    for spr in twin.get_spr_sites():
        _merge_node(client, "StrategicReserveSite", spr.id, _entity_properties(spr))
        counts["nodes"] += 1

        for refinery_id in spr.supported_refinery_ids:
            if _merge_relationship(
                client, "StrategicReserveSite", spr.id, "CAN_SUPPORT", "Refinery", refinery_id
            ):
                counts["relationships"] += 1
            else:
                logger.warning("SPR site %s references unknown refinery %s", spr.id, refinery_id)
                counts["validation_warnings"] += 1

    logger.info("Knowledge graph seed load complete: %s", counts)
    return counts


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(load_seed_graph())
