# EnergyShield AI - Knowledge Graph Schema

Human-readable companion to `backend/graph/schema.cypher` (Phase 3). The
graph is the relationship layer between suppliers, routes, chokepoints,
ports, refineries, risks, scenarios, and recommendations (Planning
Principle #6) - risk scoring, scenario modelling, and procurement
recommendation query it instead of hardcoding relationships.

## Node Types

Every node's Pydantic model (`backend/models/digital_twin_schema.py`) is
written into the graph verbatim via `entity.model_dump(by_alias=True)`
(`backend/graph/seed_graph.py::_entity_properties`), so the property names
below are exactly the model's field names - there is no separate
graph-only naming convention.

| Node Label | Represents | Key Properties |
| --- | --- | --- |
| `Commodity` | A tracked commodity (`CommodityType`) | `entity_id`, `name` |
| `SupplierCountry` | A crude-exporting country | `entity_id`, `name`, `region`, `import_share_percent`, `data_source`, `is_simulated` |
| `SupplierCompany` | A company-level supplier (future depth beyond MVP) | `entity_id`, `name`, `country` |
| `ExportPort` | Origin loading port/terminal | `entity_id`, `name`, `country`, `coordinates` |
| `ShippingRoute` | A maritime route between an export port and an import port | `entity_id`, `origin_port_id`, `destination_port_id`, `distance_km`, `estimated_transit_days`, `risk_level` |
| `Chokepoint` | A maritime chokepoint or route waypoint | `entity_id`, `name`, `importance_score`, `risk_level` |
| `ImportPort` | Indian receiving port | `entity_id`, `name`, `state`, `coordinates` |
| `Refinery` | Indian refinery | `entity_id`, `name`, `owner`, `capacity_bpd`, `location_name` |
| `StrategicReserveSite` | Indian strategic petroleum reserve (SPR) cavern | `entity_id`, `name`, `capacity_mmbbl`, `drawdown_priority` |
| `CrudeGrade` | A crude oil grade/quality class | `entity_id`, `name` |
| `RiskEvent` | A structured event from the event extraction agent (Phase 4) | `event_id`, `event_type`, `severity`, `confidence`, `detected_at` |
| `SanctionEntity` | A sanctioned country, entity, vessel, or bank | `entity_id`, `name`, `list_type` |
| `Scenario` | A scenario run (Phase 6) | `scenario_id`, `scenario_type`, `confidence` |
| `Recommendation` | A generated procurement/SPR recommendation (Phase 7) | `recommendation_id`, `confidence` |
| `DemandSector` | A downstream demand category (e.g. transport fuel, petrochemicals) | `entity_id`, `name` |

This is intentionally a small ontology (10-12 core node types per the
plan's risk register - "Knowledge graph becomes overcomplicated") so it
stays fast to query and easy to extend for Phase 14 commodities.

## Relationship Types

| Relationship | From Node | To Node | Meaning |
| --- | --- | --- | --- |
| `SUPPLIES` | `SupplierCountry` | `Commodity` | Country exports this commodity to India |
| `EXPORTS_FROM` | `SupplierCountry` | `ExportPort` | Country's crude is loaded at this port |
| `USES_ROUTE` | `ExportPort` | `ShippingRoute` | Cargo from this port travels this route |
| `TRANSITS` | `ShippingRoute` | `Chokepoint` | Route passes through this chokepoint/waypoint |
| `ARRIVES_AT` | `ShippingRoute` | `ImportPort` | Route terminates at this Indian port |
| `FEEDS` | `ImportPort` | `Refinery` | Port supplies crude to this refinery |
| `ACCEPTS_GRADE` | `Refinery` | `CrudeGrade` | Refinery is configured to process this grade |
| `PRODUCES_GRADE` | `SupplierCountry` | `CrudeGrade` | Country's crude is of this grade |
| `CAN_SUPPORT` | `StrategicReserveSite` | `Refinery` | Reserve site can draw down to supply this refinery |
| `AFFECTS` | `RiskEvent` | `Chokepoint` / `ShippingRoute` / `SupplierCountry` | Event has a modelled impact on this entity |
| `LINKED_TO` | `SanctionEntity` | `SupplierCountry` | Sanction is associated with this supplier country |
| `TRIGGERED_BY` | `Scenario` | `RiskEvent` | Scenario run was initiated by this event |
| `MITIGATES` | `Recommendation` | `Scenario` | Recommendation addresses this scenario's impact |
| `USES_ROUTE` | `Recommendation` | `ShippingRoute` | Recommendation proposes routing cargo this way |

`AFFECTS` edges carry `confidence`, `severity`, and `detected_at`
properties, plus `expired_at` (set on resolution, left `NULL` while the
event is still active) so `relationship_builder.py` can expire stale event
impact without deleting the historical `RiskEvent` node itself (needed for
Phase 13 backtesting and audit replay).

**Known gap**: `CrudeGrade`, `ACCEPTS_GRADE`, and `PRODUCES_GRADE` are
declared in `backend/graph/schema.cypher` and the loading code for them
already exists in `backend/graph/seed_graph.py`, but no seed file
currently populates `SupplierCountry.supported_crude_grade_ids` or
`Refinery.accepted_crude_grade_ids` - so today the graph never actually
creates a `CrudeGrade` node or either relationship. This doesn't block any
checked Phase 2/3 validation item (crude-grade compatibility is a
Long-Term Extension item, not an MVP requirement), but it means the
ontology below is aspirational for that one entity type until a crude
grade seed dataset is added.

## Seed Data to Graph Mapping

`backend/graph/seed_graph.py` loads `data/seeds/*.csv` and
`data/seeds/*.geojson` into these node/relationship types:

| Seed File | Populates |
| --- | --- |
| `crude_suppliers.csv` | `SupplierCountry` nodes, `SUPPLIES`/`EXPORTS_FROM` edges, default `USES_ROUTE` linkage (no `PRODUCES_GRADE` edges yet - see "Known gap" above) |
| `export_ports.csv` | `ExportPort` nodes, `EXPORTS_FROM` edges |
| `import_ports.csv` | `ImportPort` nodes |
| `refineries.csv` | `Refinery` nodes, `FEEDS` edges from their import port(s) (no `ACCEPTS_GRADE` edges yet - see "Known gap" above) |
| `spr_sites.csv` | `StrategicReserveSite` nodes, `CAN_SUPPORT` edges from `supported_refinery_ids` |
| `chokepoints.geojson` | `Chokepoint` nodes with their polygon/point geometry |
| `routes.geojson` | `ShippingRoute` nodes, `USES_ROUTE`, `TRANSITS`, and `ARRIVES_AT` edges |

## Example Cypher Queries

These mirror the required functions in `backend/graph/graph_queries.py`.

### 1. Refineries exposed to a chokepoint closure

`get_refineries_exposed_to_chokepoint(chokepoint_id)` - used by risk
scoring (Phase 5) and the Energy Map's exposure highlighting.

```cypher
MATCH (c:Chokepoint {entity_id: $chokepoint_id})<-[:TRANSITS]-(route:ShippingRoute)
      -[:ARRIVES_AT]->(port:ImportPort)-[:FEEDS]->(refinery:Refinery)
RETURN DISTINCT refinery.entity_id AS entity_id, refinery.name AS name,
       refinery.risk_level AS risk_level, route.entity_id AS via_route_id;
```

### 2. Alternative suppliers for a disrupted/blocked supplier

`get_alternative_suppliers(commodity, blocked_supplier_id)` - used by the
procurement agent (Phase 7) to find same-commodity suppliers that are not
currently affected by any active event.

```cypher
MATCH (alt:SupplierCountry)-[:SUPPLIES]->(:Commodity {entity_id: $commodity})
WHERE alt.entity_id <> $blocked_supplier_id
OPTIONAL MATCH (alt)-[:PRODUCES_GRADE]->(grade:CrudeGrade)
OPTIONAL MATCH (:RiskEvent)-[r:AFFECTS]->(alt) WHERE r.expired_at IS NULL
WITH alt, collect(DISTINCT grade.entity_id) AS crude_grade_ids, count(r) AS active_event_count
WHERE active_event_count = 0
RETURN alt.entity_id AS entity_id, alt.name AS name, alt.region AS region,
       alt.import_share_percent AS import_share_percent, crude_grade_ids
ORDER BY alt.import_share_percent DESC;
```

Note this filters only by commodity + absence of an active `AFFECTS` edge,
not by shared crude grade - `crude_grade_ids` is returned for display but
is always empty today (see the `CrudeGrade` "Known gap" above).

### 3. Routes available for a given supplier

`get_routes_for_supplier(supplier_id)` - used by route ranking (Phase 7)
and the Energy Map.

```cypher
MATCH (s:SupplierCountry {entity_id: $supplier_id})-[:EXPORTS_FROM]->(:ExportPort)
      -[:USES_ROUTE]->(route:ShippingRoute)
RETURN DISTINCT route.entity_id AS entity_id, route.name AS name,
       route.risk_level AS risk_level, route.estimated_transit_days AS estimated_transit_days,
       route.distance_km AS distance_km;
```

### 4. Scenarios triggered by a specific event

`get_scenarios_triggered_by_event(event_id)` - used by the audit trail and
dashboard to show why a scenario ran.

```cypher
MATCH (scenario:Scenario)-[:TRIGGERED_BY]->(:RiskEvent {entity_id: $event_id})
RETURN scenario.entity_id AS entity_id, scenario.scenario_type AS scenario_type,
       scenario.confidence AS confidence;
```

### 5. Strategic reserve sites that can support a refinery

`get_spr_sites_for_refinery(refinery_id)` - used by the SPR optimizer
(Phase 7).

```cypher
MATCH (spr:StrategicReserveSite)-[:CAN_SUPPORT]->(:Refinery {entity_id: $refinery_id})
RETURN spr.entity_id AS entity_id, spr.name AS name, spr.capacity_mmbbl AS capacity_mmbbl,
       spr.drawdown_priority AS drawdown_priority
ORDER BY spr.drawdown_priority ASC;
```

## Notes on Data Quality in the Graph

`SupplierCountry` nodes carry `data_source` (e.g. `"official"`,
`"estimated"`) and a separate `is_simulated` boolean, copied straight from
`crude_suppliers.csv` - there is no single unified `data_quality` property,
and `Refinery`/`StrategicReserveSite` nodes carry no data-quality field at
all today. Queries and downstream scoring must propagate whatever
provenance a node does carry into `confidence`/`assumptions` rather than
treating graph results as ground truth (Planning Principles #4 and #9).
