# EnergyShield AI - Knowledge Graph Schema

Human-readable companion to `backend/graph/schema.cypher` (Phase 3). The
graph is the relationship layer between suppliers, routes, chokepoints,
ports, refineries, risks, scenarios, and recommendations (Planning
Principle #6) - risk scoring, scenario modelling, and procurement
recommendation query it instead of hardcoding relationships.

## Node Types

| Node Label | Represents | Key Properties |
| --- | --- | --- |
| `Commodity` | A tracked commodity (`CommodityType`) | `commodity_type` |
| `SupplierCountry` | A crude-exporting country | `entity_id`, `name`, `region`, `import_share_percent`, `data_quality` |
| `SupplierCompany` | A company-level supplier (future depth beyond MVP) | `entity_id`, `name`, `country` |
| `ExportPort` | Origin loading port/terminal | `entity_id`, `name`, `country`, `latitude`, `longitude` |
| `ShippingRoute` | A maritime route between an export port and an import port | `entity_id`, `route_id`, `distance_notes` |
| `Chokepoint` | A maritime chokepoint or route waypoint | `entity_id`, `name`, `risk_note` |
| `ImportPort` | Indian receiving port | `entity_id`, `name`, `state`, `latitude`, `longitude` |
| `Refinery` | Indian refinery | `entity_id`, `name`, `owner_type`, `capacity_mbpd`, `data_quality` |
| `StrategicReserveSite` | Indian strategic petroleum reserve (SPR) cavern | `entity_id`, `name`, `capacity_mmt`, `data_quality` |
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

`AFFECTS` edges carry `confidence` and `created_at`/`expires_at` properties
so `relationship_builder.py` can expire stale event impact without
deleting the historical `RiskEvent` node itself (needed for Phase 13
backtesting and audit replay).

## Seed Data to Graph Mapping

`backend/graph/seed_graph.py` loads `data/seeds/*.csv` and
`data/seeds/*.geojson` into these node/relationship types:

| Seed File | Populates |
| --- | --- |
| `crude_suppliers.csv` | `SupplierCountry` nodes, `PRODUCES_GRADE` edges to `CrudeGrade`, default `USES_ROUTE` linkage |
| `export_ports.csv` | `ExportPort` nodes, `EXPORTS_FROM` edges |
| `import_ports.csv` | `ImportPort` nodes |
| `refineries.csv` | `Refinery` nodes, `FEEDS` edges from their `import_port_id` |
| `spr_sites.csv` | `StrategicReserveSite` nodes, `CAN_SUPPORT` edges from `linked_refinery_ids` |
| `chokepoints.geojson` | `Chokepoint` nodes with their polygon/point geometry |
| `routes.geojson` | `ShippingRoute` nodes, `USES_ROUTE`, `TRANSITS`, and `ARRIVES_AT` edges |

## Example Cypher Queries

These mirror the required functions in `backend/graph/graph_queries.py`.

### 1. Refineries exposed to a chokepoint closure

`get_refineries_exposed_to_chokepoint(chokepoint_id)` - used by risk
scoring (Phase 5) and the Energy Map's exposure highlighting.

```cypher
MATCH (c:Chokepoint {entity_id: $chokepoint_id})<-[:TRANSITS]-(r:ShippingRoute)
      -[:ARRIVES_AT]->(p:ImportPort)-[:FEEDS]->(ref:Refinery)
RETURN DISTINCT ref.entity_id AS refinery_id,
       ref.name AS refinery_name,
       ref.capacity_mbpd AS capacity_mbpd,
       collect(DISTINCT r.route_id) AS exposed_via_routes
ORDER BY ref.capacity_mbpd DESC;
```

### 2. Alternative suppliers for a disrupted/blocked supplier

`get_alternative_suppliers(commodity, blocked_supplier_id)` - used by the
procurement agent (Phase 7) to find compatible-grade suppliers that are not
currently affected by a high-severity event.

```cypher
MATCH (blocked:SupplierCountry {entity_id: $blocked_supplier_id})
      -[:PRODUCES_GRADE]->(grade:CrudeGrade)
      <-[:PRODUCES_GRADE]-(alt:SupplierCountry)
WHERE alt.entity_id <> $blocked_supplier_id
  AND NOT EXISTS {
        MATCH (alt)<-[:AFFECTS]-(e:RiskEvent)
        WHERE e.severity >= 4 AND e.expires_at > datetime()
      }
RETURN alt.entity_id AS supplier_id, alt.name AS supplier_name,
       grade.name AS shared_grade, alt.import_share_percent AS current_share
ORDER BY alt.import_share_percent DESC;
```

### 3. Routes available for a given supplier

`get_routes_for_supplier(supplier_id)` - used by route ranking (Phase 7)
and the Energy Map.

```cypher
MATCH (s:SupplierCountry {entity_id: $supplier_id})-[:EXPORTS_FROM]->(ep:ExportPort)
      -[:USES_ROUTE]->(route:ShippingRoute)-[:ARRIVES_AT]->(ip:ImportPort)
OPTIONAL MATCH (route)-[:TRANSITS]->(cp:Chokepoint)
RETURN route.route_id AS route_id, ep.name AS export_port,
       ip.name AS import_port, collect(cp.entity_id) AS chokepoints;
```

### 4. Scenarios triggered by a specific event

`get_scenarios_triggered_by_event(event_id)` - used by the audit trail and
dashboard to show why a scenario ran.

```cypher
MATCH (sc:Scenario)-[:TRIGGERED_BY]->(e:RiskEvent {event_id: $event_id})
RETURN sc.scenario_id AS scenario_id, sc.scenario_type AS scenario_type,
       sc.confidence AS confidence;
```

### 5. Strategic reserve sites that can support a refinery

`get_spr_sites_for_refinery(refinery_id)` - used by the SPR optimizer
(Phase 7).

```cypher
MATCH (site:StrategicReserveSite)-[:CAN_SUPPORT]->(ref:Refinery {entity_id: $refinery_id})
RETURN site.entity_id AS site_id, site.name AS site_name,
       site.capacity_mmt AS capacity_mmt, site.data_quality AS data_quality;
```

## Notes on Data Quality in the Graph

Every `SupplierCountry`, `Refinery`, and `StrategicReserveSite` node carries
a `data_quality` property copied straight from the seed CSVs
(`actual`, `estimated`, or `simulated`). Queries and downstream scoring must
propagate this into `confidence`/`assumptions` rather than treating graph
results as ground truth (Planning Principles #4 and #9).
