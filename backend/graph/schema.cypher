// EnergyShield AI - Neo4j graph schema (Phase 3 knowledge graph foundation)
//
// Defines uniqueness constraints and indexes for the graph ontology described
// in ENERGYSHIELD_IMPLEMENTATION_PLAN.md Phase 3 ("Graph Ontology"). Run this
// script once against an empty Neo4j database before backend/graph/seed_graph.py.

// ---------------------------------------------------------------------------
// Uniqueness constraints - one entity_id per node label
// ---------------------------------------------------------------------------
CREATE CONSTRAINT commodity_entity_id IF NOT EXISTS FOR (n:Commodity) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT supplier_country_entity_id IF NOT EXISTS FOR (n:SupplierCountry) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT supplier_company_entity_id IF NOT EXISTS FOR (n:SupplierCompany) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT export_port_entity_id IF NOT EXISTS FOR (n:ExportPort) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT shipping_route_entity_id IF NOT EXISTS FOR (n:ShippingRoute) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT chokepoint_entity_id IF NOT EXISTS FOR (n:Chokepoint) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT import_port_entity_id IF NOT EXISTS FOR (n:ImportPort) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT refinery_entity_id IF NOT EXISTS FOR (n:Refinery) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT strategic_reserve_site_entity_id IF NOT EXISTS FOR (n:StrategicReserveSite) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT crude_grade_entity_id IF NOT EXISTS FOR (n:CrudeGrade) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT risk_event_entity_id IF NOT EXISTS FOR (n:RiskEvent) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT sanction_entity_entity_id IF NOT EXISTS FOR (n:SanctionEntity) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT scenario_entity_id IF NOT EXISTS FOR (n:Scenario) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT recommendation_entity_id IF NOT EXISTS FOR (n:Recommendation) REQUIRE n.entity_id IS UNIQUE;
CREATE CONSTRAINT demand_sector_entity_id IF NOT EXISTS FOR (n:DemandSector) REQUIRE n.entity_id IS UNIQUE;

// ---------------------------------------------------------------------------
// Indexes - name, type, commodity, risk_level, country (Phase 3, section 3.1)
// ---------------------------------------------------------------------------
CREATE INDEX supplier_country_name IF NOT EXISTS FOR (n:SupplierCountry) ON (n.name);
CREATE INDEX export_port_country IF NOT EXISTS FOR (n:ExportPort) ON (n.country);
CREATE INDEX import_port_country IF NOT EXISTS FOR (n:ImportPort) ON (n.country);
CREATE INDEX refinery_country IF NOT EXISTS FOR (n:Refinery) ON (n.country);
CREATE INDEX chokepoint_risk_level IF NOT EXISTS FOR (n:Chokepoint) ON (n.risk_level);
CREATE INDEX shipping_route_risk_level IF NOT EXISTS FOR (n:ShippingRoute) ON (n.risk_level);
CREATE INDEX risk_event_type IF NOT EXISTS FOR (n:RiskEvent) ON (n.type);
CREATE INDEX commodity_commodity IF NOT EXISTS FOR (n:Commodity) ON (n.commodity);
CREATE INDEX scenario_commodity IF NOT EXISTS FOR (n:Scenario) ON (n.commodity);

// ---------------------------------------------------------------------------
// Relationship types (Phase 3, "Graph Ontology" -> "Relationship Types")
//
// (:SupplierCountry)-[:SUPPLIES]->(:Commodity)
// (:SupplierCountry)-[:EXPORTS_FROM]->(:ExportPort)
// (:ExportPort)-[:USES_ROUTE]->(:ShippingRoute)
// (:ShippingRoute)-[:TRANSITS]->(:Chokepoint)
// (:ShippingRoute)-[:ARRIVES_AT]->(:ImportPort)
// (:ImportPort)-[:FEEDS]->(:Refinery)
// (:Refinery)-[:ACCEPTS_GRADE]->(:CrudeGrade)
// (:SupplierCountry)-[:PRODUCES_GRADE]->(:CrudeGrade)
// (:StrategicReserveSite)-[:CAN_SUPPORT]->(:Refinery)
// (:RiskEvent)-[:AFFECTS]->(:Chokepoint)
// (:RiskEvent)-[:AFFECTS]->(:ShippingRoute)
// (:RiskEvent)-[:AFFECTS]->(:SupplierCountry)
// (:SanctionEntity)-[:LINKED_TO]->(:SupplierCountry)
// (:Scenario)-[:TRIGGERED_BY]->(:RiskEvent)
// (:Recommendation)-[:MITIGATES]->(:Scenario)
// (:Recommendation)-[:USES_ROUTE]->(:ShippingRoute)
// ---------------------------------------------------------------------------
