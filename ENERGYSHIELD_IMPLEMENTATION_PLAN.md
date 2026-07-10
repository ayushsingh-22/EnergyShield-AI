# EnergyShield AI - Implementation Plan

> Phased development roadmap for an AI-driven energy supply chain resilience platform for import-dependent economies. The plan is written in an implementation-first format so coding agents and team members can directly map phases to files, modules, APIs, inputs, outputs, validation checks, and ownership.

---

## Project Scope

**Project Name**: EnergyShield AI

**Problem Statement**: AI-Driven Energy Supply Chain Resilience for Import-Dependent Economies

**Initial MVP Focus**: India's crude-oil import disruption resilience

**Long-Term Platform Scope**:

1. Crude oil supply disruption intelligence
2. Knowledge graph for supplier-route-risk-refinery relationships
3. Continuous learning from past disruptions
4. Expansion into LNG, coal, fertilizers, and critical minerals

**Core Product Promise**:

EnergyShield AI converts fast-changing geopolitical, maritime, sanctions, commodity, and logistics signals into structured risk events, corridor and supplier risk scores, disruption scenario simulations, procurement rerouting recommendations, and strategic reserve action plans.

---

## Team Ownership

| Role                                          | Person             | Core Responsibility                                                                                                                                          |
| --------------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Frontend and Backend Lead                     | Ayush Kumar        | Frontend dashboard, backend APIs, database integration, report generation, deployment, user experience, and light AI integration                             |
| ML and Agents Lead                            | Abhishek Choudhary | Event extraction, risk scoring, scenario modelling, ML evaluation, continuous learning, AI agents, explainability                                            |
| Data, Orchestration, and Knowledge Graph Lead | Mayur Raj          | Data ingestion, schedulers, workflow orchestration, source freshness, knowledge graph construction, procurement orchestration, multi-commodity data adapters |

---

## Planning Principles

The original scope is an AI-powered energy supply chain resilience system. The updated scope keeps the crude-oil MVP but expands EnergyShield AI into a persistent energy security intelligence platform.

Non-negotiable product decisions for the next build:

1. Build a long-term decision-support platform, not a one-time hackathon dashboard.
2. Start with crude oil for India, but keep the data model commodity-agnostic.
3. Treat real-time news as unreliable until validated by multiple sources.
4. Every signal must store source, timestamp, freshness, reliability, confidence, and evidence URL.
5. Every recommendation must show assumptions and explain why it was generated.
6. Use a knowledge graph as the relationship layer between suppliers, routes, chokepoints, ports, refineries, risks, scenarios, and recommendations.
7. Continuous learning must improve model weights using historical disruptions, backtests, and human feedback.
8. Multi-commodity expansion must reuse the same platform architecture through adapters, not separate codebases.
9. Mark simulated values clearly, especially refinery contracts, exact cargo details, tanker availability, and crude-grade compatibility.
10. Keep all interfaces frozen through Pydantic schemas so frontend, backend, ML, and orchestration work can run in parallel.

---

## Phase Overview

```text
PHASE 0  -> Foundation and architecture
PHASE 1  -> Data ingestion foundation
PHASE 2  -> Energy supply chain digital twin
PHASE 3  -> Knowledge graph foundation
PHASE 4  -> Geopolitical event extraction agent
PHASE 5  -> Corridor and supplier risk scoring engine
PHASE 6  -> Disruption scenario modeller
PHASE 7  -> Adaptive procurement and SPR recommendation agents
PHASE 8  -> Backend APIs and persistence
PHASE 9  -> Frontend dashboard and user experience
PHASE 10 -> End-to-end orchestration and automation
PHASE 11 -> Explainability, audit trail, and evaluation
PHASE 12 -> MVP integration, deployment, and demo
PHASE 13 -> Continuous learning from past disruptions
PHASE 14 -> Multi-commodity expansion: LNG, coal, fertilizer, critical minerals
PHASE 15 -> Final presentation, documentation, and resume packaging
```

---

## Parallel Development Track

```text
PHASE 0 - Foundation
  |
  |-- PHASE 1 - Data ingestion foundation ------------------|
  |                                                          |
  |-- PHASE 8 - Backend APIs with mock data -----------------|
  |                                                          |
  |-- PHASE 9 - Frontend dashboard with mock APIs -----------|
  |                                                          |
  v                                                          v
PHASE 2 - Digital twin                              PHASE 4 - Event extraction
  |                                                          |
  v                                                          v
PHASE 3 - Knowledge graph --------------------> PHASE 5 - Risk scoring
                                                       |
                                                       v
                                             PHASE 6 - Scenario modelling
                                                       |
                                                       v
                                      PHASE 7 - Procurement and SPR agents
                                                       |
                                                       v
                                      PHASE 10 - End-to-end orchestration
                                                       |
                                                       v
                                      PHASE 11 - Evaluation and audit
                                                       |
                                                       v
                                      PHASE 12 - MVP demo deployment
                                                       |
                                                       v
                                      PHASE 13 - Continuous learning
                                                       |
                                                       v
                                      PHASE 14 - Multi-commodity platform
```

---

## Recommended Repository Structure

```text
energyshield-ai/
  backend/
    api/
      routes/
        health.py
        data_sources.py
        digital_twin.py
        graph.py
        events.py
        risk.py
        scenarios.py
        recommendations.py
        reports.py
        learning.py
        commodities.py
    agents/
      event_extraction_agent.py
      entity_resolution_agent.py
      geopolitical_risk_agent.py
      procurement_agent.py
      spr_agent.py
      report_agent.py
    commodities/
      base_adapter.py
      crude_oil_adapter.py
      lng_adapter.py
      coal_adapter.py
      fertilizer_adapter.py
      critical_minerals_adapter.py
    db/
      migrations/
      session.py
      init_db.py
    evaluation/
      backtest_metrics.py
      event_extraction_eval.py
      scenario_eval.py
      recommendation_eval.py
    graph/
      schema.cypher
      seed_graph.py
      kg_client.py
      relationship_builder.py
      graph_queries.py
      risk_graph_updater.py
    ingestion/
      source_registry.py
      gdelt_collector.py
      maritime_alert_collector.py
      sanctions_collector.py
      commodity_price_collector.py
      ais_collector.py
      portwatch_collector.py
      import_baseline_collector.py
      data_normalizer.py
    learning/
      disruption_case_library.py
      feature_store.py
      label_builder.py
      model_trainer.py
      backtesting.py
      feedback_service.py
      model_registry.py
    models/
      core_schema.py
      data_source_schema.py
      digital_twin_schema.py
      graph_schema.py
      event_schema.py
      risk_schema.py
      scenario_schema.py
      recommendation_schema.py
      learning_schema.py
      commodity_schema.py
    optimization/
      procurement_optimizer.py
      route_ranker.py
      spr_optimizer.py
    orchestration/
      scheduler.py
      workflows.py
      event_bus.py
      job_status.py
    reports/
      report_builder.py
      templates/
    risk/
      risk_scoring_engine.py
      exposure_model.py
      reliability_model.py
      anomaly_model.py
    scenarios/
      scenario_engine.py
      impact_model.py
      templates/
        hormuz_partial_closure.yaml
        red_sea_shipping_disruption.yaml
        opec_supply_cut.yaml
        sanctions_shock.yaml
        port_congestion.yaml
        lng_supply_shock.yaml
        coal_import_disruption.yaml
        fertilizer_feedstock_shock.yaml
        critical_mineral_export_restriction.yaml
    services/
      audit_service.py
      digital_twin_service.py
      event_service.py
      risk_service.py
      scenario_service.py
      recommendation_service.py
      report_service.py
    tests/
  frontend/
    src/
      api/
        energyShieldApi.js
        mockData.js
      components/
        layout/
        maps/
        risk/
        scenarios/
        recommendations/
        graph/
        reports/
        learning/
        commodities/
      pages/
        Login.jsx
        Dashboard.jsx
        EnergyMap.jsx
        RiskMonitor.jsx
        ScenarioSimulator.jsx
        RecommendationCenter.jsx
        KnowledgeGraphExplorer.jsx
        LearningCenter.jsx
        CommodityCommandCenter.jsx
        Reports.jsx
  data/
    seeds/
      crude_suppliers.csv
      refineries.csv
      import_ports.csv
      export_ports.csv
      chokepoints.geojson
      spr_sites.csv
      commodity_definitions.yaml
      demo_disruption_cases.json
  docs/
    API_REFERENCE.md
    ARCHITECTURE.md
    DATA_SOURCE_PLAN.md
    KNOWLEDGE_GRAPH_SCHEMA.md
    SCENARIO_ASSUMPTIONS.md
    CONTINUOUS_LEARNING.md
    MULTI_COMMODITY_ROADMAP.md
    DEMO_SCRIPT.md
  docker-compose.yml
  .env.example
  README.md
```

---

# PHASE 0 - FOUNDATION

**Owner**: Ayush Kumar

**Support**: Abhishek Choudhary, Mayur Raj

**Duration**: Week 1

**Prerequisite**: None

## Objectives

- Initialize repository with frontend, backend, data, docs, and deployment folders.
- Freeze MVP scope: India crude-oil import disruption risk.
- Define schemas shared across backend, ML, graph, orchestration, and frontend.
- Define initial data sources and update frequency.
- Define 5 demo scenarios.
- Establish coding conventions for coding agents.

## Deliverables

| File or Module                              | Owner    | Description                                                                  |
| ------------------------------------------- | -------- | ---------------------------------------------------------------------------- |
| `README.md`                               | Ayush    | Project overview, quick start, architecture summary                          |
| `.env.example`                            | Ayush    | Environment variables for API keys, database, graph DB, and scheduler        |
| `docker-compose.yml`                      | Ayush    | Local development containers for backend, frontend, PostgreSQL, Neo4j, Redis |
| `backend/models/core_schema.py`           | Ayush    | Shared base schemas and enums                                                |
| `backend/models/data_source_schema.py`    | Mayur    | Data source, source reliability, freshness, and raw record schemas           |
| `backend/models/event_schema.py`          | Abhishek | Risk event and extraction schemas                                            |
| `backend/models/scenario_schema.py`       | Abhishek | Scenario request and scenario output schemas                                 |
| `backend/models/recommendation_schema.py` | Mayur    | Procurement and SPR recommendation schemas                                   |
| `docs/API_REFERENCE.md`                   | Ayush    | Frozen API contract for frontend and backend integration                     |
| `docs/SCENARIO_ASSUMPTIONS.md`            | Abhishek | Explicit assumptions for all scenario templates                              |
| `docs/DATA_SOURCE_PLAN.md`                | Mayur    | Data sources, refresh frequency, fallback strategy                           |
| `docs/ARCHITECTURE.md`                    | Ayush    | Full system architecture and component ownership                             |

## Core Enums to Define

```python
CommodityType = Literal[
    "CRUDE_OIL",
    "LNG",
    "COAL",
    "FERTILIZER",
    "CRITICAL_MINERALS"
]

RiskEventType = Literal[
    "MARITIME_ATTACK",
    "PORT_CLOSURE",
    "SANCTION_UPDATE",
    "OPEC_SUPPLY_CUT",
    "PRICE_SPIKE",
    "AIS_REROUTING",
    "CHOKEPOINT_CONGESTION",
    "REFINERY_SUPPLY_RISK",
    "EXPORT_RESTRICTION",
    "WEATHER_DISRUPTION",
    "POLITICAL_INSTABILITY"
]

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "SEVERE", "CRITICAL"]

SourceReliability = Literal["OFFICIAL", "HIGH", "MEDIUM", "LOW", "SIMULATED"]
```

## Initial API Contract

```text
GET  /api/v1/health
GET  /api/v1/data/freshness
GET  /api/v1/events/latest
GET  /api/v1/risk/corridors
GET  /api/v1/risk/suppliers
GET  /api/v1/digital-twin/map
GET  /api/v1/graph/entity/{entity_id}
POST /api/v1/scenarios/run
GET  /api/v1/scenarios/{scenario_id}
GET  /api/v1/recommendations/{scenario_id}
POST /api/v1/reports/generate
```

## Coding-Agent Instructions

- Use Pydantic models for every API request and response.
- Every function should include type hints.
- Every collector should return a normalized object even if the external source fails.
- Never drop raw source metadata.
- Any simulated data must include `is_simulated: true`.
- Every agent output must be valid JSON.
- Any LLM-generated output must have deterministic fallback logic.
- Any recommendation must include evidence, assumptions, confidence, and audit ID.

## Success Criteria

- All team members can run `docker-compose up --build`.
- API schemas are frozen for MVP.
- Frontend can start against mock API responses.
- Data ingestion, ML agents, graph, and dashboard teams have clear file ownership.

---

# PHASE 1 - DATA SOURCE SETUP AND INGESTION FOUNDATION

**Owner**: Mayur Raj

**Support**: Ayush Kumar, Abhishek Choudhary

**Duration**: Week 1-2

**Prerequisite**: Phase 0 complete

## Objectives

- Build source connectors for free/open prototype data.
- Normalize fast-changing news and official alerts into a common raw record format.
- Maintain data freshness, source reliability, and ingestion logs.
- Provide clean inputs for event extraction, risk scoring, and graph updates.

## Data Sources for MVP

| Signal Type                         | Prototype Source                                          | Update Frequency   | Reliability Tier  |
| ----------------------------------- | --------------------------------------------------------- | ------------------ | ----------------- |
| Global news and geopolitical events | GDELT or configured RSS feeds                             | 15-30 minutes      | Medium            |
| Maritime security alerts            | UKMTO, MARAD, MSCIO, IMB or manually seeded alert samples | 15-30 minutes      | Official or High  |
| Sanctions                           | OFAC, EU, UN lists or manually seeded snapshots           | Daily              | Official          |
| Oil prices                          | EIA or FRED daily Brent/WTI data                          | Daily              | High              |
| Chokepoint and port activity        | IMF PortWatch or seeded trend data                        | Weekly             | High              |
| AIS vessel movement                 | AISStream or sample AIS files                             | Live or batch demo | Low to Medium     |
| India crude import baseline         | PPAC, TradeStat, manually curated CSV                     | Monthly/manual     | High or Simulated |
| Geospatial layers                   | OSM, Natural Earth, manually curated GeoJSON              | Static/manual      | High              |

## Deliverables

| File or Module                                     | Owner | Description                                                           |
| -------------------------------------------------- | ----- | --------------------------------------------------------------------- |
| `backend/ingestion/source_registry.py`           | Mayur | Central registry of source URLs, refresh intervals, reliability tiers |
| `backend/ingestion/gdelt_collector.py`           | Mayur | Collects news records from GDELT/RSS style sources                    |
| `backend/ingestion/maritime_alert_collector.py`  | Mayur | Collects or imports maritime advisory records                         |
| `backend/ingestion/sanctions_collector.py`       | Mayur | Downloads or imports sanctions list snapshots                         |
| `backend/ingestion/commodity_price_collector.py` | Mayur | Pulls crude price time series or reads seeded price files             |
| `backend/ingestion/ais_collector.py`             | Mayur | Reads AIS stream or sample AIS records for chokepoint monitoring      |
| `backend/ingestion/portwatch_collector.py`       | Mayur | Reads chokepoint and port activity trends                             |
| `backend/ingestion/import_baseline_collector.py` | Mayur | Loads India import share and baseline demand data                     |
| `backend/ingestion/data_normalizer.py`           | Mayur | Converts all raw data into common normalized schemas                  |
| `backend/models/data_source_schema.py`           | Mayur | Schemas for raw records, normalized records, source freshness         |
| `backend/api/routes/data_sources.py`             | Ayush | Data freshness and source health endpoints                            |

## Sequence

### 1.1 `source_registry.py` - Source Registry

- **Priority**: P0
- **Task**: Create a single source registry for all data connectors.
- **Input**: Static YAML or Python config of data sources.
- **Processing**:
  1. Store source name, category, URL, refresh frequency, reliability tier, and fallback mode.
  2. Expose a function `get_active_sources()`.
  3. Expose a function `get_source_reliability(source_name)`.
- **Output**: Source metadata used by collectors and risk scoring.

### 1.2 `gdelt_collector.py` - News Ingestion

- **Priority**: P0
- **Task**: Collect latest geopolitical and energy risk news.
- **Input**: Keywords for Hormuz, Red Sea, Suez, OPEC, sanctions, crude oil, tanker, port closure.
- **Processing**:
  1. Query latest articles or read seeded article samples.
  2. Deduplicate by URL or normalized title hash.
  3. Store publication timestamp, detected timestamp, title, summary, URL, source, language, and location if available.
- **Output**: List of `RawSourceRecord` objects.

### 1.3 `maritime_alert_collector.py` - Maritime Advisory Ingestion

- **Priority**: P0
- **Task**: Collect official or high-confidence maritime alerts.
- **Input**: Advisory feeds or seeded alert JSON.
- **Processing**:
  1. Parse alert text, timestamp, location, and threat type.
  2. Map location to known chokepoint if possible.
  3. Mark reliability as `OFFICIAL` or `HIGH`.
- **Output**: Maritime alert records for event extraction.

### 1.4 `sanctions_collector.py` - Sanctions Ingestion

- **Priority**: P0
- **Task**: Track sanctions affecting suppliers, vessels, ports, banks, or energy firms.
- **Input**: Sanctions list snapshots.
- **Processing**:
  1. Parse sanctioned entity name, country, list type, effective date, and source.
  2. Detect new records compared with previous snapshot.
  3. Emit `SANCTION_UPDATE` candidate signals.
- **Output**: Sanctions delta records.

### 1.5 `commodity_price_collector.py` - Crude Price Data

- **Priority**: P1
- **Task**: Pull or load daily crude price time series.
- **Input**: Brent/WTI daily prices.
- **Processing**:
  1. Compute 1-day, 3-day, and 7-day percentage changes.
  2. Detect price spikes over configured threshold.
  3. Emit price anomaly records.
- **Output**: Price movement signals.

### 1.6 `data_normalizer.py` - Common Normalized Schema

- **Priority**: P0
- **Task**: Convert all source outputs to normalized records.
- **Input**: Raw records from collectors.
- **Processing**:
  1. Add normalized timestamp fields.
  2. Add `source_reliability`.
  3. Add `commodity_type` where possible.
  4. Add `geo_hint` and `corridor_hint` where possible.
  5. Preserve raw text and source URL.
- **Output**: `NormalizedSignal` records.

## Phase 1 Validation

- ✅ Each collector runs independently without crashing.
- ✅ Each record includes source, timestamp, reliability, raw text, and detected time.
- ✅ Duplicate news records are removed.
- ✅ Failed sources are logged but do not break the full pipeline.
- ✅ `/api/v1/data/freshness` shows last update time for each source.

## Phase 1 Completion Status

Status:
✅ Completed

Completion Date:
2026-07-09

Implementation Summary

List every completed module:

✓ source_registry.py
✓ gdelt_collector.py
✓ maritime_alert_collector.py
✓ sanctions_collector.py
✓ commodity_price_collector.py
✓ ais_collector.py
✓ portwatch_collector.py
✓ import_baseline_collector.py
✓ data_normalizer.py
✓ backend/api/routes/data_sources.py

New Features Added

• Central Source Registry
• BaseCollector abstraction
• RawSourceRecord model
• NormalizedSignal pipeline
• Commodity-agnostic ingestion
• Structured logging
• Deduplication engine
• Source health monitoring
• Freshness tracking
• API endpoints for ingestion health

Architecture Improvements

The ingestion framework is now reusable across:
Crude Oil
LNG
Coal
Fertilizer
Critical Minerals
without code duplication.

Lessons Learned

- why normalized records were introduced: To standardize heterogeneous data streams into a single structure that downstream components and AI agents can process uniformly.
- why collectors inherit from BaseCollector: To enforce a consistent contract for fetching, normalizing, and health-checking, ensuring graceful failure and preventing pipeline crashes.
- why metadata preservation is mandatory: To maintain full auditability, allowing every generated insight, score, or recommendation to trace back to its original source, confidence, and timestamp.
- why the ingestion layer is commodity agnostic: To allow the exact same codebase to support LNG, Coal, Fertilizer, and Critical Minerals merely by adding new adapters, avoiding duplicate architecture.

Future Integration

Phase 2 (Digital Twin) will consume NormalizedSignal objects directly from this ingestion pipeline.

---

# PHASE 2 - ENERGY SUPPLY CHAIN DIGITAL TWIN

**Owner**: Mayur Raj

**Support**: Ayush Kumar, Abhishek Choudhary

**Duration**: Week 2

**Prerequisite**: Phase 1 started; Phase 0 schemas finalized

## Objectives

- Build the geospatial and relational model of the crude-oil supply network.
- Represent suppliers, export ports, chokepoints, routes, import ports, refineries, and SPR sites.
- Provide the baseline exposure model used by risk scoring and scenario simulation.

## Deliverables

| File or Module                               | Owner | Description                                                          |
| -------------------------------------------- | ----- | -------------------------------------------------------------------- |
| `backend/models/digital_twin_schema.py`    | Mayur | Pydantic schemas for suppliers, ports, routes, refineries, SPR sites |
| `backend/services/digital_twin_service.py` | Mayur | Query and update digital twin entities                               |
| `backend/api/routes/digital_twin.py`       | Ayush | APIs for map layers and entity details                               |
| `data/seeds/crude_suppliers.csv`           | Mayur | Supplier country and region seed data                                |
| `data/seeds/export_ports.csv`              | Mayur | Export port seed data                                                |
| `data/seeds/import_ports.csv`              | Mayur | Indian import port seed data                                         |
| `data/seeds/refineries.csv`                | Mayur | Refinery location and capacity seed data                             |
| `data/seeds/spr_sites.csv`                 | Mayur | Strategic reserve site seed data                                     |
| `data/seeds/chokepoints.geojson`           | Mayur | Hormuz, Bab el-Mandeb, Suez, Cape route, Malacca if needed           |
| `data/seeds/routes.geojson`                | Mayur | Approximate route geometries                                         |

## Core Entities

```text
SupplierCountry
ExportPort
ShippingRoute
Chokepoint
ImportPort
Refinery
StrategicReserveSite
Commodity
CrudeGrade
DemandSector
```

## Sequence

### 2.1 Supplier and Import Baseline

- **Priority**: P0
- **Task**: Create baseline crude import exposure table.
- **Input**: `crude_suppliers.csv`, import shares, route assumptions.
- **Processing**:
  1. Define supplier country/region.
  2. Assign import share and default route.
  3. Mark import share as public, estimated, or simulated.
- **Output**: Supplier exposure baseline.

### 2.2 Route and Chokepoint Layer

- **Priority**: P0
- **Task**: Create route geometries and chokepoint polygons.
- **Input**: GeoJSON seed files.
- **Processing**:
  1. Store each route as a line string.
  2. Store each chokepoint as polygon or bounding box.
  3. Link route to one or more chokepoints.
- **Output**: Map-ready route and chokepoint layers.

### 2.3 Refinery and SPR Layer

- **Priority**: P0
- **Task**: Represent Indian refineries and reserve sites.
- **Input**: `refineries.csv`, `spr_sites.csv`.
- **Processing**:
  1. Store coordinates, capacity, owner type, and crude flexibility assumptions.
  2. Link refineries to import ports and possible supplier routes.
  3. Store SPR capacity and drawdown assumptions.
- **Output**: Refinery and reserve layer for scenario modelling.

### 2.4 Digital Twin API

- **Priority**: P0
- **Task**: Expose map and entity data to frontend.
- **Endpoints**:

```text
GET /api/v1/digital-twin/map
GET /api/v1/digital-twin/suppliers
GET /api/v1/digital-twin/routes
GET /api/v1/digital-twin/chokepoints
GET /api/v1/digital-twin/refineries
GET /api/v1/digital-twin/exposure
```

## Phase 2 Validation

- ✅ Map can display supplier regions, routes, chokepoints, Indian ports, refineries, and SPR sites.
- ✅ Every supplier has at least one route.
- ✅ Every route has at least one chokepoint or route risk zone.
- ✅ Every refinery has coordinates and a capacity assumption.
- ✅ Exposure percentages are marked as actual, estimated, or simulated.

## Phase 2 Completion Status

Status:
✅ Completed

Completion Date:
2026-07-09

Implementation Summary

Completed modules:

✓ backend/models/digital_twin_schema.py
✓ backend/services/digital_twin_service.py
✓ backend/api/routes/digital_twin.py
✓ data/seeds/crude_suppliers.csv
✓ data/seeds/export_ports.csv
✓ data/seeds/import_ports.csv
✓ data/seeds/refineries.csv
✓ data/seeds/spr_sites.csv
✓ data/seeds/routes.geojson
✓ data/seeds/chokepoints.geojson

New Features Added

• Commodity-agnostic Digital Twin data model
• Supplier exposure baseline
• Shipping route network
• Chokepoint intelligence layer
• Indian import infrastructure model
• Refinery dependency model
• Strategic Petroleum Reserve representation
• GeoJSON-ready API responses
• Deterministic exposure calculations

Architecture Improvements

The Digital Twin is now the canonical source of truth for:

- Suppliers
- Routes
- Ports
- Chokepoints
- Refineries
- SPR Sites

Phase 3 (Knowledge Graph) will consume these entities directly rather than recreating them.

Lessons Learned

- why the Digital Twin is commodity-agnostic: To ensure the same architecture, schemas, and API endpoints can handle LNG, coal, and critical minerals effortlessly in future phases.
- why deterministic exposure calculations precede AI-based risk scoring: Because accurate mathematical baselines (e.g., exact % import dependencies) are required as hard facts to ground the AI's risk modeling and prevent hallucinations.
- why GeoJSON is returned directly from backend: To minimize frontend transformation logic and keep the presentation layer lightweight, instantly rendering spatial entities.
- why entities have stable IDs for future graph relationships: Stable, cross-commodity IDs guarantee that when Phase 3 loads these into Neo4j, edges between nodes can be strictly typed and persistently referenced.

Future Integration

Phase 3 will build Neo4j relationships using the Digital Twin entities created in Phase 2.

---

# PHASE 3 - KNOWLEDGE GRAPH FOUNDATION

**Owner**: Mayur Raj

**Support**: Abhishek Choudhary, Ayush Kumar

**Duration**: Week 2-3

**Prerequisite**: Phase 2 core entities available

## Objectives

- Add a knowledge graph for supplier-route-risk-refinery relationships.
- Make the system answer relationship-heavy questions like:
  - Which refineries are exposed to Strait of Hormuz disruption?
  - Which suppliers can replace a high-risk supplier for a compatible crude grade?
  - Which routes are affected by a new maritime event?
  - Which strategic reserve sites can support affected refineries?
- Feed graph context into risk scoring, scenario modelling, and procurement recommendation.

## Deliverables

| File or Module                                    | Owner    | Description                                                            |
| ------------------------------------------------- | -------- | ---------------------------------------------------------------------- |
| `backend/graph/schema.cypher`                   | Mayur    | Neo4j node labels, relationship types, constraints, indexes            |
| `backend/graph/seed_graph.py`                   | Mayur    | Loads digital twin seed data into graph DB                             |
| `backend/graph/kg_client.py`                    | Mayur    | Graph DB client wrapper                                                |
| `backend/graph/relationship_builder.py`         | Mayur    | Builds relationships from suppliers, routes, ports, refineries, events |
| `backend/graph/graph_queries.py`                | Mayur    | Reusable graph query functions                                         |
| `backend/graph/risk_graph_updater.py`           | Abhishek | Updates graph with risk scores and active events                       |
| `backend/models/graph_schema.py`                | Mayur    | Pydantic schemas for graph nodes, edges, query results                 |
| `backend/api/routes/graph.py`                   | Ayush    | Graph query APIs for frontend and agents                               |
| `docs/KNOWLEDGE_GRAPH_SCHEMA.md`                | Mayur    | Human-readable graph schema and query examples                         |
| `frontend/src/pages/KnowledgeGraphExplorer.jsx` | Ayush    | Optional graph explorer UI                                             |

## Graph Ontology

### Node Types

```text
Commodity
SupplierCountry
SupplierCompany
ExportPort
ShippingRoute
Chokepoint
ImportPort
Refinery
StrategicReserveSite
CrudeGrade
RiskEvent
SanctionEntity
Scenario
Recommendation
DemandSector
```

### Relationship Types

```text
(:SupplierCountry)-[:SUPPLIES]->(:Commodity)
(:SupplierCountry)-[:EXPORTS_FROM]->(:ExportPort)
(:ExportPort)-[:USES_ROUTE]->(:ShippingRoute)
(:ShippingRoute)-[:TRANSITS]->(:Chokepoint)
(:ShippingRoute)-[:ARRIVES_AT]->(:ImportPort)
(:ImportPort)-[:FEEDS]->(:Refinery)
(:Refinery)-[:ACCEPTS_GRADE]->(:CrudeGrade)
(:SupplierCountry)-[:PRODUCES_GRADE]->(:CrudeGrade)
(:StrategicReserveSite)-[:CAN_SUPPORT]->(:Refinery)
(:RiskEvent)-[:AFFECTS]->(:Chokepoint)
(:RiskEvent)-[:AFFECTS]->(:ShippingRoute)
(:RiskEvent)-[:AFFECTS]->(:SupplierCountry)
(:SanctionEntity)-[:LINKED_TO]->(:SupplierCountry)
(:Scenario)-[:TRIGGERED_BY]->(:RiskEvent)
(:Recommendation)-[:MITIGATES]->(:Scenario)
(:Recommendation)-[:USES_ROUTE]->(:ShippingRoute)
```

## Sequence

### 3.1 `schema.cypher` - Graph Schema

- **Priority**: P0
- **Task**: Define graph node labels, relationships, uniqueness constraints, and indexes.
- **Input**: Digital twin entity list.
- **Processing**:
  1. Add unique constraints for `entity_id`.
  2. Add indexes on `name`, `type`, `commodity`, `risk_level`, and `country`.
  3. Define relationship names consistently.
- **Output**: Graph schema ready for seed loading.

### 3.2 `seed_graph.py` - Seed Knowledge Graph

- **Priority**: P0
- **Task**: Load seed data into Neo4j.
- **Input**: CSV and GeoJSON digital twin seed files.
- **Processing**:
  1. Create nodes for suppliers, ports, routes, chokepoints, refineries, SPR sites, grades.
  2. Create baseline relationships.
  3. Validate that each route connects origin to destination.
- **Output**: Initial graph database.

### 3.3 `relationship_builder.py` - Dynamic Relationship Updates

- **Priority**: P0
- **Task**: Convert new risk events into graph edges.
- **Input**: Structured `RiskEvent` records.
- **Processing**:
  1. Link event to affected country, port, chokepoint, route, supplier, or refinery.
  2. Add `AFFECTS` edge with confidence and timestamp.
  3. Expire old event edges when event is resolved.
- **Output**: Current risk-aware graph.

### 3.4 `graph_queries.py` - Reusable Queries

- **Priority**: P0
- **Task**: Implement graph queries used by risk and recommendation agents.
- **Required functions**:

```python
def get_refineries_exposed_to_chokepoint(chokepoint_id: str) -> list[dict]:
    pass

def get_alternative_suppliers(commodity: str, blocked_supplier_id: str) -> list[dict]:
    pass

def get_routes_for_supplier(supplier_id: str) -> list[dict]:
    pass

def get_scenarios_triggered_by_event(event_id: str) -> list[dict]:
    pass

def get_spr_sites_for_refinery(refinery_id: str) -> list[dict]:
    pass
```

### 3.5 `risk_graph_updater.py` - Risk-Aware Graph Updates

- **Priority**: P1
- **Task**: Store corridor, supplier, and refinery risk scores back into graph nodes.
- **Input**: Risk score results from Phase 5.
- **Processing**:
  1. Update `risk_score`, `risk_level`, `last_risk_update` on nodes.
  2. Create `HAS_RISK_SCORE` history edges if needed.
  3. Keep latest score queryable by frontend.
- **Output**: Graph-powered risk context.

## API Contract

```text
GET  /api/v1/graph/entity/{entity_id}
GET  /api/v1/graph/refineries-exposed?chokepoint_id=HORMUZ
GET  /api/v1/graph/alternative-suppliers?supplier_id=IRAN&commodity=CRUDE_OIL
GET  /api/v1/graph/routes?supplier_id=SAUDI_ARABIA
POST /api/v1/graph/query-impact
```

## Phase 3 Validation

- [x] Query can identify all refineries exposed to a chosen chokepoint.
- [x] Query can produce alternative suppliers for a disrupted supplier.
- [x] New risk events create `AFFECTS` edges in the graph.
- [ ] Scenario engine can use graph queries instead of hardcoded relationships. (Blocked on Phase 6 - scenario engine doesn't exist yet.)
- [ ] Frontend can display at least one graph-driven exposure view. (Deferred to Phase 9 per the "Optional" note on `KnowledgeGraphExplorer.jsx`.)

## Phase 3 Completion Status

Status:
✅ Completed (backend graph layer). Frontend explorer and Phase 5/6 integration remain future work as noted above.

Completion Date:
2026-07-09

Implementation Summary

List every completed module:

✓ backend/graph/schema.cypher (already present from initial scaffolding - constraints/indexes verified against the Phase 3 ontology)
✓ backend/graph/kg_client.py
✓ backend/graph/seed_graph.py
✓ backend/graph/relationship_builder.py
✓ backend/graph/graph_queries.py
✓ backend/models/graph_schema.py (added `ImpactQueryRequest`)
✓ backend/api/routes/graph.py
✓ backend/main.py (wired `graph`, `data_sources`, `digital_twin` routers - the latter two were implemented in Phase 1/2 but never registered)
✓ backend/tests/graph/test_graph_queries.py
✓ backend/tests/graph/test_relationship_builder.py
✓ backend/tests/graph/test_seed_graph.py
✓ backend/tests/api/test_graph.py
✓ docs/API_REFERENCE.md (Knowledge Graph section flipped to Live; also fixed stale Planned status on already-shipped Digital Twin and `/data/freshness` rows)

New Features Added

• Neo4j client wrapper with graceful degradation (queries return `[]` and log a warning instead of crashing when Neo4j is unreachable, matching the ingestion `BaseCollector` contract)
• Idempotent MERGE-based graph seeding from the Phase 2 `DigitalTwinService` (suppliers, ports, routes, chokepoints, refineries, SPR sites, commodities)
• Route origin/destination validation warnings during seeding (logged, not fatal)
• RiskEvent -> `AFFECTS` edge creation and expiry (edges are marked `expired_at` rather than deleted, preserving history for Phase 13 continuous learning)
• The 5 required reusable query functions plus generic entity-neighborhood and bounded-hop impact-traversal queries
• 5 knowledge graph API endpoints per the frozen contract

Architecture Improvements

The knowledge graph is now the relationship layer described in Planning
Principle #6: risk scoring, scenario modelling, and procurement
recommendation can query `backend/graph/graph_queries.py` instead of
hardcoding which refineries/suppliers/routes are connected to what.

Lessons Learned

- why every graph write uses MERGE instead of CREATE: re-running the seed loader against an already-seeded database must update properties, not duplicate nodes/edges - this keeps seeding safe to run repeatedly during development and in CI.
- why AFFECTS edges are expired instead of deleted: Phase 13's continuous-learning track needs the historical record of what an event affected, even after the event resolves.
- why `kg_client.run_query` swallows exceptions and returns `[]`: an unreachable graph database must degrade the API (empty results) rather than crash it, mirroring how ingestion collectors already treat unreachable external sources.
- why the graph-explorer frontend page and risk-graph-updater module were left untouched: they depend on Phase 9 (frontend integration) and Phase 5 (risk scores) respectively, which don't exist yet - their stubs already say as much.
- Testing caveat: this sandbox has no Python packages installed (no `pip`/`poetry` available) and no running Neo4j instance, so these modules were verified by syntax-checking (`py_compile`) and by unit tests against a mocked `KGClient`, not by executing against a live graph. Run `poetry install && docker compose up neo4j && pytest backend/tests/graph backend/tests/api/test_graph.py` in a real environment to confirm end-to-end.

Future Integration

Phase 4's event extraction agent will call `relationship_builder.upsert_event_relationships` for every extracted event. Phase 5's risk scoring engine will populate `backend/graph/risk_graph_updater.py` (still a stub) and read `graph_queries` for exposure. Phase 6/7 will call the alternative-supplier and SPR queries directly instead of hardcoding relationships.

---

# PHASE 4 - GEOPOLITICAL EVENT EXTRACTION AGENT

**Owner**: Abhishek Choudhary

**Support**: Mayur Raj, Ayush Kumar

**Duration**: Week 3-4

**Prerequisite**: Phase 1 normalized signals available; Phase 3 graph schema available

## Objectives

- Convert unstructured news, maritime alerts, sanctions, AIS anomalies, and price spikes into structured risk events.
- Resolve event entities to graph nodes.
- Assign severity, confidence, and scenario trigger candidates.

## Deliverables

| File or Module                                | Owner    | Description                                                                |
| --------------------------------------------- | -------- | -------------------------------------------------------------------------- |
| `backend/agents/event_extraction_agent.py`  | Abhishek | Main extraction pipeline for structured risk events                        |
| `backend/agents/entity_resolution_agent.py` | Abhishek | Links event text to supplier, route, chokepoint, port, refinery, commodity |
| `backend/ml/event_classifier.py`            | Abhishek | Rule-based or ML event classifier                                          |
| `backend/services/event_service.py`         | Abhishek | Event persistence and retrieval logic                                      |
| `backend/models/event_schema.py`            | Abhishek | `RiskEvent`, `EventEvidence`, `ExtractionResult` schemas             |
| `backend/api/routes/events.py`              | Ayush    | Latest event feed and event detail APIs                                    |
| `prompts/risk_event_extraction.md`          | Abhishek | LLM prompt for structured extraction                                       |

## Risk Event Output Schema

```json
{
  "event_id": "EVT-2026-0001",
  "event_type": "MARITIME_ATTACK",
  "commodity_type": "CRUDE_OIL",
  "title": "Tanker incident reported near Red Sea corridor",
  "summary": "Structured summary of the event",
  "published_at": "2026-07-06T09:00:00Z",
  "detected_at": "2026-07-06T09:15:00Z",
  "source_name": "UKMTO_OR_GDELT",
  "source_reliability": "HIGH",
  "location_name": "Red Sea / Bab el-Mandeb",
  "latitude": 12.6,
  "longitude": 43.3,
  "affected_entities": ["RED_SEA_ROUTE", "BAB_EL_MANDEB"],
  "severity": 4,
  "confidence": 0.82,
  "scenario_triggers": ["RED_SEA_SHIPPING_DISRUPTION"],
  "evidence_urls": ["source-url-or-placeholder"],
  "is_simulated": false
}
```

## Sequence

### 4.1 Event Taxonomy

- **Priority**: P0
- **Task**: Define event types and trigger rules.
- **Input**: Problem scenarios and source types.
- **Processing**:
  1. Map source keywords to event types.
  2. Define severity scale 1-5.
  3. Define trigger candidates for scenarios.
- **Output**: Event taxonomy config.

### 4.2 Event Extraction

- **Priority**: P0
- **Task**: Extract structured fields from raw text.
- **Input**: `NormalizedSignal`.
- **Processing**:
  1. Use deterministic rules for official alerts and sanctions.
  2. Use LLM or NLP model for messy news text.
  3. Validate JSON output against `RiskEvent` schema.
  4. Fall back to keyword-based extraction if LLM fails.
- **Output**: `RiskEvent`.

### 4.3 Entity Resolution

- **Priority**: P0
- **Task**: Link event to knowledge graph nodes.
- **Input**: Event location, country, supplier, route, port, commodity.
- **Processing**:
  1. Match entity names to graph aliases.
  2. Map coordinates to nearest chokepoint or route polygon.
  3. Add entity IDs to event.
- **Output**: Graph-linked risk event.

### 4.4 Confidence and Source Weighting

- **Priority**: P0
- **Task**: Calculate confidence score.
- **Input**: Source reliability, number of corroborating sources, text quality, location match.
- **Processing**:
  1. Official source increases confidence.
  2. Multiple independent sources increase confidence.
  3. Missing location decreases confidence.
  4. Simulated source marks event as demo-only.
- **Output**: Confidence score in range 0-1.

## Phase 4 Validation

- [x] Agent converts at least 20 seeded news/alert records into structured events. (`backend/tests/agents/test_event_extraction_agent.py::test_extract_batch_converts_at_least_twenty_signals_with_high_resolution` runs 22 synthetic signals through `EventExtractionAgent.extract_batch` and asserts >=20 succeed.)
- [x] Every event has event type, source, timestamp, severity, confidence, and affected entity. (Same test asserts `event_type`, `source_name`, `detected_at`, `severity` in 1-5, and `confidence` in 0-1 on every successfully extracted `RiskEvent`; `affected_entities` is populated whenever the signal's text resolves - see next bullet for the resolution rate.)
- [x] Entity resolution links at least 80% of test events to a graph node. (Same test computes `resolution_rate = resolved / succeeded` over the 22-signal fixture and asserts `>= 0.8`; entity ids resolved by `EntityResolutionAgent` are the same `entity_id`s seeded into Neo4j by `graph/seed_graph.py`.)
- [x] LLM failure fallback produces valid schema output. (`test_extract_falls_back_when_llm_returns_invalid_json` and `test_extract_falls_back_when_llm_omits_event_type` feed a fake Anthropic client invalid/incomplete responses and assert `extraction_method == "rule_based_fallback"` with a valid `RiskEvent` still produced.)
- [x] Frontend can show latest structured event feed. (`GET /api/v1/events/latest` wired into `backend/main.py`; `frontend/src/api/energyShieldApi.js::getLatestEvents` and the "Phase 4 Latest Events" panel in `frontend/src/App.jsx` render it, with `mockLatestEvents` populated in `frontend/src/api/mockData.js` for the `VITE_USE_MOCK_DATA=true` default.)

## Phase 4 Completion Status

Status:
✅ Completed

Completion Date:
2026-07-10

Implementation Summary

List every completed module:

✓ backend/ml/event_classifier.py (new - event taxonomy, section 4.1)
✓ backend/agents/entity_resolution_agent.py
✓ backend/agents/event_extraction_agent.py
✓ backend/services/event_service.py
✓ backend/api/routes/events.py
✓ prompts/risk_event_extraction.md
✓ backend/main.py (wired the `events` router)
✓ backend/tests/agents/test_event_classifier.py
✓ backend/tests/agents/test_entity_resolution_agent.py
✓ backend/tests/agents/test_event_extraction_agent.py
✓ backend/tests/services/test_event_service.py
✓ backend/tests/api/test_events.py
✓ docs/API_REFERENCE.md (Events section flipped to Live)
✓ frontend/src/api/energyShieldApi.js (added `getLatestEvents`)
✓ frontend/src/api/mockData.js (populated `mockLatestEvents`)
✓ frontend/src/App.jsx (added the Phase 4 Latest Events panel)

New Features Added

• Deterministic event taxonomy: keyword-to-event-type rules, per-type severity
  base with intensity adjustment, and chokepoint/event-type -> MVP scenario
  trigger mapping
• Entity resolution against the Phase 2 Digital Twin's in-memory seed data
  (chokepoints, suppliers, refineries, import ports, routes), with a
  hand-curated alias table for common news shorthand (e.g. "Hormuz", "Red
  Sea"), chokepoint-to-route expansion, and chokepoint-polygon-centroid
  coordinate resolution
• Three-path extraction pipeline - `official_alert_direct` (deterministic
  rules for OFFICIAL/HIGH sources), `llm` (Anthropic client, only attempted
  when configured), and `rule_based_fallback` (same deterministic rules,
  used whenever the LLM is unavailable or its output fails schema
  validation) - so a missing API key or a bad LLM response never breaks
  the pipeline
• Confidence scoring from source reliability, resolved-location/entity
  presence, and a simulated-data cap (section 4.4)
- `GET /api/v1/events/latest` and `GET /api/v1/events/{event_id}`, backed by
  an in-memory `EventService` and a pipeline that runs the six Phase 1
  collectors through the normalizer and extraction agent once at import
  time - the same load-once-at-import pattern `digital_twin.py` already uses
- Every extracted event is pushed into the knowledge graph via
  `graph.relationship_builder.upsert_event_relationships`, the Phase 3
  integration point that had been unused until now

Architecture Improvements

Event extraction closes the loop the Phase 3 completion notes called out as
still open: `NormalizedSignal` records now flow all the way through to
graph `AFFECTS` edges without any manual step. Because entity resolution
runs against the Digital Twin's in-memory data rather than requiring a live
graph query, the whole pipeline (ingestion -> normalize -> extract -> graph
link) degrades gracefully with no Neo4j running, matching the
already-established `KGClient` graceful-degradation contract.

Lessons Learned

- why entity resolution matches against `DigitalTwinService` instead of
  querying Neo4j: extraction must stay testable and functional without a
  live graph database, exactly like ingestion collectors and `KGClient`
  already do; the resolved ids are identical to what `seed_graph.py` loads,
  so `relationship_builder.upsert_event_relationships` still links correctly
  once a real graph is running.
- why confidence and scenario triggers are always computed deterministically,
  even on the `llm` path: the plan's confidence formula (section 4.4) is
  about source reliability and corroboration, not the model's self-rated
  confidence, and scenario triggers depend on knowledge-graph structure the
  LLM has no visibility into - only `event_type`, `title`, `summary`, and
  `severity` are taken from the model's output.
- why the "at least 20 records" and "80% resolution" checkpoints are
  validated with a synthetic 22-signal test fixture rather than the live
  Phase 1 collectors: each seeded collector still returns exactly one demo
  record (by design, from Phase 1), so proving the checkpoints against the
  live pipeline would either require inflating Phase 1's owned seed data or
  accepting a thin, unrepresentative demo feed; a dedicated test fixture
  proves the extraction agent's actual capability independent of how many
  demo records Phase 1 happens to seed today.
- Testing caveat: this environment has no running Neo4j instance, so the
  events pipeline's graph-write step was verified via the existing
  mocked-`KGClient` test pattern (`relationship_builder` tests) plus manual
  import-time verification showing graceful `AFFECTS`-edge-skip warnings
  logged instead of a crash. Run against a live Neo4j (`docker compose up
  neo4j`) to confirm real edges are created end-to-end.

Future Integration

Phase 5's risk scoring engine can read the same `RiskEvent.severity`,
`source_reliability`, and graph `AFFECTS` edges this phase now produces
instead of needing its own event ingestion. Phase 6's scenario engine can
key off `RiskEvent.scenario_triggers` directly rather than re-deriving
trigger conditions from raw event data.

---

# PHASE 5 - CORRIDOR AND SUPPLIER RISK SCORING ENGINE

**Owner**: Abhishek Choudhary

**Support**: Mayur Raj

**Duration**: Week 4

**Prerequisite**: Phase 4 event extraction working; Phase 3 graph query functions available

## Objectives

- Generate live risk scores for corridors, suppliers, routes, ports, refineries, and commodities.
- Use event severity, source reliability, India exposure, AIS anomaly, commodity price movement, and graph exposure.
- Store current and historical risk scores.

## Deliverables

| File or Module                          | Owner    | Description                                       |
| --------------------------------------- | -------- | ------------------------------------------------- |
| `backend/risk/risk_scoring_engine.py` | Abhishek | Main risk score computation                       |
| `backend/risk/exposure_model.py`      | Abhishek | India exposure and refinery exposure calculations |
| `backend/risk/reliability_model.py`   | Abhishek | Source reliability and corroboration weighting    |
| `backend/risk/anomaly_model.py`       | Abhishek | AIS and price anomaly features                    |
| `backend/services/risk_service.py`    | Abhishek | Stores and retrieves risk scores                  |
| `backend/graph/risk_graph_updater.py` | Abhishek | Updates graph with latest risk scores             |
| `backend/api/routes/risk.py`          | Ayush    | Risk card and risk history APIs                   |

## Initial Risk Formula

```text
Risk Score =
  0.30 * Event Severity Score
+ 0.20 * Source Reliability Score
+ 0.20 * Import Exposure Score
+ 0.15 * Route or AIS Anomaly Score
+ 0.15 * Commodity Price Movement Score
```

## Risk Score Output Schema

```json
{
  "entity_id": "HORMUZ",
  "entity_type": "CHOKEPOINT",
  "commodity_type": "CRUDE_OIL",
  "risk_score": 82.0,
  "risk_level": "HIGH",
  "previous_score": 48.0,
  "delta": 34.0,
  "top_drivers": [
    "High-severity maritime event",
    "High India import exposure",
    "Price spike detected"
  ],
  "evidence_event_ids": ["EVT-2026-0001"],
  "updated_at": "2026-07-06T10:00:00Z"
}
```

## Sequence

### 5.1 Corridor Risk Score

- **Priority**: P0
- **Task**: Score chokepoints and routes.
- **Input**: Risk events, AIS anomalies, price movement, graph route exposure.
- **Processing**:
  1. Group active events by corridor.
  2. Compute severity-weighted event score.
  3. Add exposure from graph relationships.
  4. Add anomaly and price features.
- **Output**: Corridor risk score.

### 5.2 Supplier Risk Score

- **Priority**: P0
- **Task**: Score supplier countries and supplier companies.
- **Input**: Sanctions, political events, route exposure, import share.
- **Processing**:
  1. Link supplier to active events through graph.
  2. Add sanctions score.
  3. Add route risk for supplier's routes.
  4. Add import share exposure.
- **Output**: Supplier risk score.

### 5.3 Refinery Exposure Score

- **Priority**: P1
- **Task**: Estimate which refineries are exposed to upstream disruptions.
- **Input**: Graph route-to-port-to-refinery relationships.
- **Processing**:
  1. Query graph for refineries connected to affected routes.
  2. Weight exposure by assumed capacity and import dependency.
  3. Mark confidence based on available data.
- **Output**: Refinery-level exposure score.

### 5.4 Risk Graph Update

- **Priority**: P0
- **Task**: Push latest risk scores into the knowledge graph.
- **Input**: Risk score records.
- **Processing**:
  1. Update node properties.
  2. Create score history entries.
  3. Link scores to evidence events.
- **Output**: Queryable risk-aware graph.

## Phase 5 Validation

- [x] Risk score changes when a high-severity event is added. (`backend/tests/risk/test_risk_scoring_engine.py::test_score_corridor_risk_increases_with_high_severity_event` and `backend/tests/services/test_risk_service.py::test_score_changes_when_high_severity_event_added` inject a severity-5 event and assert the recomputed score rises.)
- [x] Risk score decreases when event is resolved or expires. (`test_risk_service.py::test_score_decreases_when_event_resolved` adds an event, confirms the score rises, then clears it via `EventService.replace_all([])` and confirms the score falls back down.)
- [x] Top drivers are understandable to a non-technical user. (`risk_scoring_engine._build_top_drivers` emits plain-language strings like "High-severity event: Maritime security incident reported in this corridor" and "High India crude import exposure via this entity (62.4% of imports)" rather than raw feature names.)
- [x] Graph nodes show latest risk score. (`backend/graph/risk_graph_updater.py::update_risk_score` `SET`s `risk_score`/`risk_level`/`last_risk_update` on the matching graph node, called from `RiskService.refresh()` whenever a score changes; verified against a fake `KGClient` in `backend/tests/graph/test_risk_graph_updater.py`.)
- [x] Risk history is stored for trend charts and continuous learning. (`RiskService` keeps a per-entity history list that only grows on an actual score change - `test_risk_service.py::test_history_grows_only_on_actual_change` - queryable via `GET /api/v1/risk/history/{entity_id}`.)

## Phase 5 Completion Status

Status:
✅ Completed

Completion Date:
2026-07-10

Implementation Summary

List every completed module:

✓ backend/risk/exposure_model.py
✓ backend/risk/reliability_model.py
✓ backend/risk/anomaly_model.py
✓ backend/risk/risk_scoring_engine.py
✓ backend/graph/risk_graph_updater.py
✓ backend/services/risk_service.py (replaced the earlier static-mock version with real computation)
✓ backend/api/routes/risk.py (wired the live Phase 4 event feed in; endpoints themselves were already frozen and unchanged)
✓ backend/api/routes/events.py (added `get_event_service()` so Phase 5 can read the live event set without re-running ingestion)
✓ backend/tests/risk/test_exposure_model.py
✓ backend/tests/risk/test_reliability_model.py
✓ backend/tests/risk/test_anomaly_model.py
✓ backend/tests/risk/test_risk_scoring_engine.py
✓ backend/tests/graph/test_risk_graph_updater.py
✓ backend/tests/services/test_risk_service.py
✓ backend/tests/api/test_risk.py (fixed one assertion that only held against the old mock's fabricated history trend)

New Features Added

• Corridor risk scoring (5.1) for every chokepoint and shipping route, from
  live `RiskEvent`s grouped by `affected_entities`, graph-equivalent import
  exposure, AIS/congestion anomaly signals, and a market-wide price-spike
  term
• Supplier risk scoring (5.2) that inherits risk from a supplier's default
  shipping route in addition to events resolved directly to the supplier
• Refinery exposure scoring (5.3): refineries reachable from a stressed
  chokepoint's routes, weighted by each refinery's share of total Indian
  refining capacity
• Knowledge-graph risk push (5.4): every changed score updates its graph
  node's `risk_score`/`risk_level`, plus a `RiskScoreSnapshot` history node
  linked back to its evidence events via `EVIDENCED_BY`
• Change-triggered risk history per entity, so `GET /risk/history/{id}`
  reflects genuine score movements instead of a fabricated demo trend

Architecture Improvements

Exposure figures are computed from the Phase 2 `DigitalTwinService`
in-memory data rather than live Neo4j queries - the same
graceful-degradation choice Phase 4's `EntityResolutionAgent` made - so
risk scores stay available with no graph database running. The numbers
are identical either way since `graph/seed_graph.py` loads the graph from
this same digital-twin data. `RiskService` recomputes on every read rather
than via a background loop, since no Phase 10 scheduler exists yet; this
is simpler and just as correct while the event set only changes when the
Phase 4 pipeline re-runs.

Lessons Learned

- why `RiskService` reads events through `api.routes.events.get_event_service()`
  rather than re-running ingestion itself: Phase 5 explicitly depends on
  "Phase 4 event extraction working" per the plan's prerequisite - reusing
  the same live event set (instead of a second independent fetch) keeps
  risk scores consistent with whatever `/events/latest` is currently
  showing.
- why a commodity price spike lifts every corridor/supplier's score
  uniformly instead of only the entity a `PRICE_SPIKE` event happens to
  resolve against: the commodity price collector has no specific
  corridor/supplier to attach a global price move to (its signals carry no
  location hint), so treating it as market-wide pressure is more honest
  than pretending it's evidence for one entity.
- why risk history only grows when the score actually changes, not on
  every read: `RiskService.get_corridors()`/`get_suppliers()` recompute on
  every call (no caching layer yet), so appending unconditionally would
  flood history with identical duplicate entries between real events.
- Testing caveat: as with Phase 3's graph writes, this sandbox has no
  running Neo4j instance, so `risk_graph_updater`'s Cypher was verified
  against a mocked `KGClient` (`backend/tests/graph/test_risk_graph_updater.py`)
  and via observing graceful "unknown entity, node update skipped" warnings
  during a real app boot, not against a live graph.

Future Integration

Phase 6's scenario engine can read `RiskScore.risk_level`/`top_drivers`
directly instead of re-deriving corridor stress from raw events. Phase 7's
procurement/SPR agents can use the same supplier and refinery scores this
phase now produces for feasibility ranking.

---

# PHASE 6 - DISRUPTION SCENARIO MODELLER

**Owner**: Abhishek Choudhary

**Support**: Mayur Raj, Ayush Kumar

**Duration**: Week 5

**Prerequisite**: Phase 5 risk scores available; Phase 3 graph queries available

## Objectives

- Simulate disruption scenarios and downstream supply impacts.
- Convert current risk conditions into what-if impact estimates.
- Make assumptions explicit and testable.

## MVP Scenarios

| Scenario                         | Scenario ID                     | Main Impact                                             |
| -------------------------------- | ------------------------------- | ------------------------------------------------------- |
| Strait of Hormuz partial closure | `HORMUZ_PARTIAL_CLOSURE`      | Middle East supply exposure, delays, price pressure     |
| Red Sea shipping disruption      | `RED_SEA_SHIPPING_DISRUPTION` | Suez route delay, Cape rerouting, freight cost increase |
| OPEC+ emergency supply cut       | `OPEC_SUPPLY_CUT`             | Supplier availability reduction, spot price pressure    |
| Sanctions shock                  | `SANCTIONS_SHOCK`             | Supplier feasibility and payment/logistics risk         |
| Indian import port congestion    | `PORT_CONGESTION`             | Arrival delays and refinery run-rate risk               |

## Deliverables

| File or Module                           | Owner    | Description                                                   |
| ---------------------------------------- | -------- | ------------------------------------------------------------- |
| `backend/scenarios/scenario_engine.py` | Abhishek | Main scenario execution engine                                |
| `backend/scenarios/impact_model.py`    | Abhishek | Calculates supply gap, delays, cost impact, refinery exposure |
| `backend/scenarios/templates/*.yaml`   | Abhishek | Scenario assumptions and parameters                           |
| `backend/services/scenario_service.py` | Abhishek | Scenario persistence and retrieval                            |
| `backend/api/routes/scenarios.py`      | Ayush    | Scenario run and history APIs                                 |
| `docs/SCENARIO_ASSUMPTIONS.md`         | Abhishek | Explanation of assumptions and limitations                    |

## Scenario Request Schema

```json
{
  "scenario_type": "HORMUZ_PARTIAL_CLOSURE",
  "commodity_type": "CRUDE_OIL",
  "duration_days": 15,
  "severity": "HIGH",
  "affected_entities": ["HORMUZ"],
  "manual_overrides": {
    "supply_reduction_percent": 25,
    "freight_cost_increase_percent": 18
  }
}
```

## Scenario Output Schema

```json
{
  "scenario_id": "SCN-2026-0001",
  "scenario_type": "HORMUZ_PARTIAL_CLOSURE",
  "commodity_type": "CRUDE_OIL",
  "duration_days": 15,
  "supply_at_risk_percent": 24.0,
  "estimated_delay_days": 9,
  "freight_cost_impact_percent": 18.0,
  "affected_refineries": [
    {
      "refinery_id": "REF-001",
      "exposure_level": "HIGH",
      "reason": "Connected to imports through affected route"
    }
  ],
  "recommended_action_required": true,
  "confidence": 0.72,
  "assumptions": [
    "Import share data is estimated",
    "Exact cargo ownership is simulated"
  ]
}
```

## Sequence

### 6.1 Scenario Template Design

- **Priority**: P0
- **Task**: Define YAML templates for each scenario.
- **Input**: Scenario assumptions.
- **Processing**:
  1. Store default duration bands.
  2. Store supply reduction parameters.
  3. Store delay and freight cost assumptions.
  4. Store affected corridors and commodities.
- **Output**: Reusable scenario config files.

### 6.2 Impact Model

- **Priority**: P0
- **Task**: Calculate supply, delay, cost, and refinery impacts.
- **Input**: Scenario request, risk scores, graph relationships.
- **Processing**:
  1. Query graph for affected routes and refineries.
  2. Estimate supply exposure using baseline imports.
  3. Estimate shipping delay using route-specific assumptions.
  4. Estimate cost impact using crude price and freight assumptions.
- **Output**: Scenario impact result.

### 6.3 Scenario Trigger Logic

- **Priority**: P1
- **Task**: Auto-trigger scenario when risk crosses threshold.
- **Input**: Risk score update.
- **Processing**:
  1. If corridor risk > threshold, find scenario templates linked to the event.
  2. Run scenario in background.
  3. Notify dashboard.
- **Output**: Triggered scenario run.

## Phase 6 Validation

- [ ] Each MVP scenario runs from API and returns valid output.
- [ ] Scenario assumptions are shown in output.
- [ ] Scenario uses graph relationships instead of hardcoded refinery lists.
- [ ] Scenario output changes when duration or severity changes.
- [ ] Scenario confidence decreases when simulated data is heavily used.

---

# PHASE 7 - ADAPTIVE PROCUREMENT AND SPR RECOMMENDATION AGENTS

**Owner**: Mayur Raj

**Support**: Abhishek Choudhary, Ayush Kumar

**Duration**: Week 6

**Prerequisite**: Phase 6 scenario results available

## Objectives

- Recommend alternate suppliers, routes, and ports after a scenario.
- Recommend strategic petroleum reserve drawdown timing and quantity.
- Convert scenario output into an executable action plan.

## Deliverables

| File or Module                                    | Owner    | Description                                            |
| ------------------------------------------------- | -------- | ------------------------------------------------------ |
| `backend/optimization/procurement_optimizer.py` | Mayur    | Ranks procurement alternatives                         |
| `backend/optimization/route_ranker.py`          | Mayur    | Scores route options by cost, delay, risk, feasibility |
| `backend/optimization/spr_optimizer.py`         | Abhishek | Suggests reserve drawdown schedules                    |
| `backend/agents/procurement_agent.py`           | Mayur    | Agent wrapper for procurement recommendations          |
| `backend/agents/spr_agent.py`                   | Abhishek | Agent wrapper for SPR recommendations                  |
| `backend/services/recommendation_service.py`    | Mayur    | Stores and retrieves recommendation outputs            |
| `backend/api/routes/recommendations.py`         | Ayush    | Recommendation APIs                                    |

## Procurement Scoring Formula

```text
Option Score =
  0.25 * Cost Efficiency
+ 0.25 * Route Safety
+ 0.20 * Supplier Reliability
+ 0.15 * Delivery Time
+ 0.15 * Refinery Compatibility
```

## Recommendation Output Schema

```json
{
  "recommendation_id": "REC-2026-0001",
  "scenario_id": "SCN-2026-0001",
  "commodity_type": "CRUDE_OIL",
  "ranked_options": [
    {
      "rank": 1,
      "supplier": "West Africa basket",
      "route": "Cape route",
      "estimated_delay_days": 6,
      "cost_impact_percent": 9.5,
      "risk_level": "MEDIUM",
      "feasibility_score": 0.78,
      "reason": "Lower chokepoint risk and acceptable refinery compatibility"
    }
  ],
  "spr_plan": {
    "drawdown_required": true,
    "start_day": 7,
    "drawdown_percent": 15,
    "reason": "Medium supply gap persists beyond one week"
  },
  "confidence": 0.70,
  "assumptions": ["Tanker availability is simulated"]
}
```

## Sequence

### 7.1 Alternative Supplier Discovery

- **Priority**: P0
- **Task**: Use graph queries to find alternate suppliers.
- **Input**: Disrupted supplier, commodity, crude grade, affected route.
- **Processing**:
  1. Query graph for suppliers producing compatible grade.
  2. Exclude suppliers affected by active high-risk events.
  3. Score suppliers by reliability and exposure.
- **Output**: Candidate supplier list.

### 7.2 Route Ranking

- **Priority**: P0
- **Task**: Rank alternate routes.
- **Input**: Candidate suppliers, current route risk, distance/delay assumptions.
- **Processing**:
  1. Query graph for available routes.
  2. Score risk, delay, cost, and port feasibility.
  3. Return ranked route options.
- **Output**: Ranked supplier-route pairs.

### 7.3 SPR Optimization

- **Priority**: P1
- **Task**: Recommend strategic reserve use.
- **Input**: Supply gap forecast, refinery demand assumptions, scenario duration.
- **Processing**:
  1. Avoid drawdown for short low-severity shocks.
  2. Recommend controlled drawdown when supply gap persists.
  3. Reserve emergency drawdown for high or critical duration scenarios.
- **Output**: SPR drawdown schedule.

### 7.4 Action Plan Generation

- **Priority**: P0
- **Task**: Convert ranked options into user-facing action plan.
- **Input**: Procurement and SPR outputs.
- **Processing**:
  1. Create concise recommendation summary.
  2. Add action priority: immediate, monitor, contingency.
  3. Include evidence and assumptions.
- **Output**: Action plan ready for frontend and report.

## Phase 7 Validation

- [ ] Recommendation is generated for every scenario.
- [ ] Recommendation includes cost, risk, delay, feasibility, and confidence.
- [ ] Recommendation uses knowledge graph alternatives.
- [ ] SPR drawdown is not triggered for every small event.
- [ ] Every recommendation includes assumptions and audit ID.

---

# PHASE 8 - BACKEND PLATFORM APIS AND PERSISTENCE

**Owner**: Ayush Kumar

**Support**: Mayur Raj, Abhishek Choudhary

**Duration**: Week 4-7, parallel with Phases 4-7

**Prerequisite**: Phase 0 API contract finalized

## Objectives

- Build backend services and database persistence.
- Expose stable APIs for frontend and orchestration.
- Maintain audit trail for every event, scenario, recommendation, and report.

## Deliverables

| File or Module                        | Owner | Description                               |
| ------------------------------------- | ----- | ----------------------------------------- |
| `backend/main.py`                   | Ayush | FastAPI app entry point                   |
| `backend/db/session.py`             | Ayush | Database session and connection handling  |
| `backend/db/migrations/`            | Ayush | Database migrations                       |
| `backend/storage/repository.py`     | Ayush | Persistence abstraction for relational DB |
| `backend/services/audit_service.py` | Ayush | Immutable audit event recording           |
| `backend/api/routes/*.py`           | Ayush | API route modules                         |
| `backend/reports/report_builder.py` | Ayush | Crisis-response report generation         |
| `backend/tests/api/`                | Ayush | API contract tests                        |

## API Endpoints

```text
GET  /api/v1/health
GET  /api/v1/data/freshness
GET  /api/v1/events/latest
GET  /api/v1/events/{event_id}
GET  /api/v1/risk/corridors
GET  /api/v1/risk/suppliers
GET  /api/v1/risk/history/{entity_id}
GET  /api/v1/digital-twin/map
GET  /api/v1/graph/entity/{entity_id}
POST /api/v1/graph/query-impact
POST /api/v1/scenarios/run
GET  /api/v1/scenarios/{scenario_id}
GET  /api/v1/recommendations/{scenario_id}
POST /api/v1/reports/generate
GET  /api/v1/audit/{entity_id}
```

## Sequence

### 8.1 Database and Repository Layer

- **Priority**: P0
- **Task**: Store entities and outputs.
- **Tables**:
  - `data_sources`
  - `raw_records`
  - `normalized_signals`
  - `risk_events`
  - `risk_scores`
  - `scenario_runs`
  - `recommendations`
  - `audit_events`
  - `generated_reports`

### 8.2 API Route Implementation

- **Priority**: P0
- **Task**: Implement API routes using service layer.
- **Processing**:
  1. Validate request with Pydantic.
  2. Call service method.
  3. Return response schema.
  4. Log audit event where needed.

### 8.3 Report Builder

- **Priority**: P1
- **Task**: Generate executive crisis-response report.
- **Input**: Event, risk score, scenario, recommendations, assumptions.
- **Output**: Markdown or PDF-ready report payload.

## Phase 8 Validation

- [ ] API docs render correctly.
- [ ] Frontend can call mock and live APIs using same response shape.
- [ ] Every scenario and recommendation is stored.
- [ ] Every recommendation has an audit trail.
- [ ] API contract tests pass.

---

# PHASE 9 - FRONTEND DASHBOARD AND USER EXPERIENCE

**Owner**: Ayush Kumar

**Support**: Mayur Raj, Abhishek Choudhary

**Duration**: Week 4-8, parallel with backend and ML

**Prerequisite**: Phase 0 API contract finalized

## Objectives

- Build a polished analyst-facing dashboard.
- Use mock API first, then switch to live backend.
- Show risk evidence, maps, graph relationships, scenarios, recommendations, and reports.

## Deliverables

| File or Module                                                      | Owner | Description                              |
| ------------------------------------------------------------------- | ----- | ---------------------------------------- |
| `frontend/src/pages/Dashboard.jsx`                                | Ayush | Main command center overview             |
| `frontend/src/pages/RiskMonitor.jsx`                              | Ayush | Corridor and supplier risk cards         |
| `frontend/src/pages/EnergyMap.jsx`                                | Ayush | Geospatial digital twin map              |
| `frontend/src/pages/ScenarioSimulator.jsx`                        | Ayush | Scenario input and results UI            |
| `frontend/src/pages/RecommendationCenter.jsx`                     | Ayush | Procurement and SPR recommendations      |
| `frontend/src/pages/KnowledgeGraphExplorer.jsx`                   | Ayush | Graph relationship explorer              |
| `frontend/src/pages/LearningCenter.jsx`                           | Ayush | Continuous learning and model version UI |
| `frontend/src/pages/CommodityCommandCenter.jsx`                   | Ayush | Multi-commodity expansion UI             |
| `frontend/src/components/maps/SupplyRouteMap.jsx`                 | Ayush | Map visualization component              |
| `frontend/src/components/risk/RiskScoreCard.jsx`                  | Ayush | Risk score cards                         |
| `frontend/src/components/scenarios/ScenarioResultPanel.jsx`       | Ayush | Scenario outputs                         |
| `frontend/src/components/recommendations/RecommendationTable.jsx` | Ayush | Ranked recommendations                   |
| `frontend/src/api/energyShieldApi.js`                             | Ayush | API client                               |
| `frontend/src/api/mockData.js`                                    | Ayush | Mock responses matching backend schemas  |

## Main Screens

### 9.1 Dashboard

- **Priority**: P0
- Show current top risks, latest events, triggered scenarios, and active recommendations.

### 9.2 Energy Map

- **Priority**: P0
- Show suppliers, routes, chokepoints, import ports, refineries, and SPR sites.
- Highlight high-risk corridors.

### 9.3 Risk Monitor

- **Priority**: P0
- Show corridor and supplier risk cards with score, level, delta, top drivers, and evidence.

### 9.4 Scenario Simulator

- **Priority**: P0
- Let user select scenario type, duration, severity, commodity, and manual assumptions.
- Display supply at risk, delay, cost impact, affected refineries, and confidence.

### 9.5 Recommendation Center

- **Priority**: P0
- Show ranked supplier-route alternatives and SPR recommendation.
- Include confidence, assumptions, and action priority.

### 9.6 Knowledge Graph Explorer

- **Priority**: P1
- Show relationship path such as:

```text
Supplier -> Export Port -> Route -> Chokepoint -> Import Port -> Refinery
```

### 9.7 Learning Center

- **Priority**: P2
- Show historical disruptions, backtest results, model versions, and feedback outcomes.

### 9.8 Commodity Command Center

- **Priority**: P2
- Show commodity selector and commodity-specific risk panels for crude oil, LNG, coal, fertilizers, and critical minerals.

## Phase 9 Validation

- [ ] All pages render with mock data.
- [ ] Map displays digital twin entities.
- [ ] Risk cards show top drivers and evidence.
- [ ] Scenario simulator can call backend and show output.
- [ ] Recommendation table is understandable without technical explanation.
- [ ] Frontend can switch from mock API to live API using environment config.

---

# PHASE 10 - END-TO-END ORCHESTRATION AND AUTOMATION

**Owner**: Mayur Raj

**Support**: Abhishek Choudhary, Ayush Kumar

**Duration**: Week 7-8

**Prerequisite**: Phases 1, 4, 5, 6, 7, and 8 substantially complete

## Objectives

- Connect collectors, event extraction, graph update, risk scoring, scenario triggering, recommendation generation, and dashboard updates.
- Turn independent modules into an automated intelligence pipeline.

## Deliverables

| File or Module                               | Owner | Description                                   |
| -------------------------------------------- | ----- | --------------------------------------------- |
| `backend/orchestration/scheduler.py`       | Mayur | Scheduled jobs for data refresh               |
| `backend/orchestration/workflows.py`       | Mayur | End-to-end pipeline definitions               |
| `backend/orchestration/event_bus.py`       | Mayur | Lightweight event bus or Redis stream wrapper |
| `backend/orchestration/job_status.py`      | Mayur | Job status tracking                           |
| `backend/workers/risk_worker.py`           | Mayur | Background risk scoring jobs                  |
| `backend/workers/scenario_worker.py`       | Mayur | Scenario trigger jobs                         |
| `backend/workers/recommendation_worker.py` | Mayur | Recommendation generation jobs                |

## Main Workflow

```text
Data collector runs
  -> normalized signals stored
  -> event extraction agent runs
  -> entity resolution links events to graph
  -> graph risk relationships updated
  -> risk scoring engine recalculates scores
  -> if threshold crossed, scenario model runs
  -> procurement and SPR agents generate recommendations
  -> dashboard receives updated state
  -> audit log records each step
```

## Sequence

### 10.1 Scheduled Data Refresh

- **Priority**: P0
- **Task**: Run collectors on configured intervals.
- **Input**: Source registry.
- **Output**: Updated normalized signals.

### 10.2 Event-Driven Agent Trigger

- **Priority**: P0
- **Task**: Trigger event extraction when new signals arrive.
- **Input**: New normalized signals.
- **Output**: New or updated risk events.

### 10.3 Risk and Graph Update

- **Priority**: P0
- **Task**: Update knowledge graph and risk scores after event extraction.
- **Input**: Risk events.
- **Output**: Current risk scores and graph relationships.

### 10.4 Scenario Auto-Trigger

- **Priority**: P1
- **Task**: Run scenario when risk crosses threshold.
- **Input**: Risk score delta and trigger rules.
- **Output**: Scenario run and recommendation generation.

### 10.5 Workflow Monitoring

- **Priority**: P1
- **Task**: Show job status and failures.
- **Input**: Scheduler and worker logs.
- **Output**: `/api/v1/data/freshness` and job dashboard.

## Phase 10 Validation

- [ ] A seeded Red Sea alert triggers event extraction.
- [ ] Extracted event updates graph relationships.
- [ ] Risk score changes automatically.
- [ ] High risk triggers a scenario run.
- [ ] Scenario generates procurement and SPR recommendations.
- [ ] Audit trail captures each step.

---

# PHASE 11 - EXPLAINABILITY, AUDIT TRAIL, AND EVALUATION

**Owner**: Abhishek Choudhary

**Support**: Ayush Kumar, Mayur Raj

**Duration**: Week 8

**Prerequisite**: Phase 10 end-to-end workflow working

## Objectives

- Explain why a risk score, scenario result, or recommendation was generated.
- Evaluate signal detection, scenario fidelity, recommendation quality, geospatial evidence depth, and end-to-end response time.
- Make every action auditable.

## Deliverables

| File or Module                                           | Owner    | Description                                         |
| -------------------------------------------------------- | -------- | --------------------------------------------------- |
| `backend/services/audit_service.py`                    | Ayush    | Audit event storage and retrieval                   |
| `backend/services/explainer_service.py`                | Abhishek | Explanation generation for risk and recommendations |
| `backend/evaluation/event_extraction_eval.py`          | Abhishek | Event extraction precision checks on seeded data    |
| `backend/evaluation/scenario_eval.py`                  | Abhishek | Scenario assumption and output validation           |
| `backend/evaluation/recommendation_eval.py`            | Abhishek | Recommendation quality checks                       |
| `backend/evaluation/backtest_metrics.py`               | Abhishek | Shared metric utilities                             |
| `frontend/src/components/reports/AuditLogTable.jsx`    | Ayush    | UI for audit trail                                  |
| `frontend/src/components/risk/ExplainabilityPanel.jsx` | Ayush    | UI showing top drivers and evidence                 |

## Evaluation Metrics

| Metric                     | How to Measure                                                                   |
| -------------------------- | -------------------------------------------------------------------------------- |
| Signal detection lead time | `detected_at - published_at`                                                   |
| Event extraction accuracy  | Correct event type, location, commodity, and affected entity on labelled samples |
| Risk score explainability  | Percentage of scores with top drivers and evidence events                        |
| Scenario fidelity          | All assumptions explicit and testable                                            |
| Recommendation quality     | Each recommendation includes cost, risk, delay, feasibility, and confidence      |
| Geospatial evidence depth  | Affected route/chokepoint/refinery visible on map                                |
| End-to-end response time   | Time from signal ingestion to recommendation generated                           |
| Auditability               | Every event, scenario, recommendation, and override has audit entry              |

## Audit Event Schema

```json
{
  "audit_id": "AUD-2026-0001",
  "entity_type": "RECOMMENDATION",
  "entity_id": "REC-2026-0001",
  "action": "GENERATED",
  "actor": "SYSTEM",
  "timestamp": "2026-07-06T10:25:00Z",
  "source_event_ids": ["EVT-2026-0001"],
  "model_version": "risk-v0.1",
  "summary": "Procurement recommendation generated after Red Sea risk score crossed threshold"
}
```

## Phase 11 Validation

- [ ] Every risk score has top drivers.
- [ ] Every scenario output has explicit assumptions.
- [ ] Every recommendation has evidence and confidence.
- [ ] Evaluation script produces summary metrics.
- [ ] Audit trail can reconstruct full path from signal to recommendation.

---

# PHASE 12 - MVP INTEGRATION, DEPLOYMENT, AND DEMO

**Owner**: Ayush Kumar

**Support**: Abhishek Choudhary, Mayur Raj

**Duration**: Week 8-9

**Prerequisite**: Phases 1-11 substantially complete

## Objectives

- Integrate frontend, backend, graph DB, database, and orchestration.
- Prepare a stable demo flow.
- Deploy prototype.
- Create README, architecture diagram, and demo script.

## Deliverables

| File or Module            | Owner | Description                                   |
| ------------------------- | ----- | --------------------------------------------- |
| `docker-compose.yml`    | Ayush | Full-stack local setup                        |
| `deploy/`               | Ayush | Deployment config                             |
| `docs/DEMO_SCRIPT.md`   | Ayush | Step-by-step demo storyline                   |
| `docs/ARCHITECTURE.md`  | Ayush | Final architecture diagram and explanation    |
| `README.md`             | Ayush | Setup, usage, data caveats, demo instructions |
| `frontend/.env.example` | Ayush | Frontend environment variables                |
| `backend/tests/e2e/`    | Ayush | End-to-end tests                              |

## Recommended Demo Flow

```text
1. Open dashboard and show current energy risk overview.
2. Show digital twin map with crude suppliers, routes, chokepoints, ports, refineries, and SPR sites.
3. Inject or select a seeded Red Sea maritime alert.
4. Event extraction agent classifies it as RED_SEA_SHIPPING_DISRUPTION.
5. Knowledge graph links the event to Red Sea route, Bab el-Mandeb, Suez route, and affected refineries.
6. Risk score increases for Red Sea/Suez corridor.
7. Scenario modeller estimates delay, cost, and supply impact.
8. Procurement agent ranks Cape route and alternate suppliers.
9. SPR agent recommends monitor or controlled drawdown depending on duration.
10. Dashboard shows action plan and generates an executive report.
```

## Phase 12 Validation

- [ ] Full demo runs without manual backend changes.
- [ ] Docker compose starts all required services.
- [ ] Frontend connects to live backend.
- [ ] Graph queries work in deployed/local demo.
- [ ] Report generation works.
- [ ] README quick start works on a clean machine.

---

# PHASE 13 - CONTINUOUS LEARNING FROM PAST DISRUPTIONS

**Owner**: Abhishek Choudhary

**Support**: Mayur Raj, Ayush Kumar

**Duration**: Sprint 10+

**Prerequisite**: Phase 12 MVP complete

## Objectives

- Learn from historical energy supply disruptions.
- Backtest risk scoring and scenario assumptions.
- Calibrate event severity, source reliability, risk thresholds, and recommendation quality over time.
- Add human feedback loops for procurement and policy experts.
- Maintain model versions so previous decisions remain auditable.

## Deliverables

| File or Module                                  | Owner    | Description                                                  |
| ----------------------------------------------- | -------- | ------------------------------------------------------------ |
| `backend/learning/disruption_case_library.py` | Abhishek | Stores curated historical disruption cases                   |
| `backend/learning/feature_store.py`           | Abhishek | Stores features used by risk and scenario models             |
| `backend/learning/label_builder.py`           | Abhishek | Converts historical outcomes into labels                     |
| `backend/learning/model_trainer.py`           | Abhishek | Trains or calibrates risk models and thresholds              |
| `backend/learning/backtesting.py`             | Abhishek | Runs past disruptions through old and new models             |
| `backend/learning/feedback_service.py`        | Abhishek | Captures analyst feedback on recommendations                 |
| `backend/learning/model_registry.py`          | Abhishek | Tracks model versions, metrics, and deployment status        |
| `backend/models/learning_schema.py`           | Abhishek | Pydantic schemas for cases, labels, feedback, model versions |
| `backend/api/routes/learning.py`              | Ayush    | Learning, feedback, and model version APIs                   |
| `frontend/src/pages/LearningCenter.jsx`       | Ayush    | UI for model versions, backtests, and feedback history       |
| `docs/CONTINUOUS_LEARNING.md`                 | Abhishek | Learning strategy, metrics, and governance                   |

## Historical Case Schema

```json
{
  "case_id": "CASE-REDSEA-2024-001",
  "case_name": "Red Sea shipping disruption sample case",
  "commodity_type": "CRUDE_OIL",
  "start_date": "2024-01-01",
  "end_date": "2024-02-15",
  "trigger_events": ["MARITIME_ATTACK", "AIS_REROUTING"],
  "affected_corridors": ["RED_SEA", "SUEZ"],
  "observed_outcomes": {
    "average_delay_days": 12,
    "freight_cost_increase_percent": 20,
    "route_shift_detected": true,
    "price_movement_percent": 6
  },
  "source_notes": "Public data or simulated historical case notes",
  "is_simulated": true
}
```

## Sequence

### 13.1 `disruption_case_library.py` - Historical Case Store

- **Priority**: P1
- **Task**: Store historical disruption cases.
- **Input**: Curated public cases or manually seeded historical scenarios.
- **Processing**:
  1. Store case metadata.
  2. Store trigger events.
  3. Store observed outcomes.
  4. Mark source quality and simulated fields.
- **Output**: Searchable disruption case library.

### 13.2 `feature_store.py` - Model Feature Store

- **Priority**: P1
- **Task**: Store features used at prediction time.
- **Input**: Risk events, source reliability, price movement, AIS anomaly, exposure, graph features.
- **Processing**:
  1. Store feature vector by timestamp and entity.
  2. Link feature vector to model version and output score.
  3. Preserve features for backtesting.
- **Output**: Reproducible feature history.

### 13.3 `label_builder.py` - Outcome Labels

- **Priority**: P1
- **Task**: Convert observed outcomes into learning labels.
- **Input**: Historical case outcomes.
- **Processing**:
  1. Label whether disruption became material.
  2. Label observed delay band.
  3. Label observed price impact band.
  4. Label whether rerouting occurred.
- **Output**: Training or calibration labels.

### 13.4 `backtesting.py` - Backtesting Harness

- **Priority**: P1
- **Task**: Replay historical cases through the current model.
- **Input**: Historical cases and feature timeline.
- **Processing**:
  1. Run risk model at each historical timestamp.
  2. Compare predicted risk with observed outcome.
  3. Compute precision, recall, false alarm rate, missed event rate, and lead time.
- **Output**: Backtest report.

### 13.5 `model_trainer.py` - Calibration and Threshold Learning

- **Priority**: P2
- **Task**: Improve risk score weights and thresholds.
- **Input**: Feature store and labels.
- **Processing**:
  1. Start with logistic regression, gradient boosting, or Bayesian calibration.
  2. Calibrate scenario trigger thresholds.
  3. Compare learned model against rule-based baseline.
  4. Store new version only if metrics improve.
- **Output**: Calibrated risk model version.

### 13.6 `feedback_service.py` - Human Feedback Loop

- **Priority**: P1
- **Task**: Capture analyst feedback on recommendations.
- **Input**: User feedback from dashboard.
- **Processing**:
  1. Record whether recommendation was useful.
  2. Record accepted, rejected, or modified action.
  3. Capture reason for rejection or override.
  4. Feed future learning and evaluation.
- **Output**: Feedback dataset.

### 13.7 `model_registry.py` - Versioning and Governance

- **Priority**: P1
- **Task**: Track model versions and deployment status.
- **Input**: Trained models, rule versions, metrics.
- **Processing**:
  1. Store model version, training data range, metrics, and owner.
  2. Mark version as `candidate`, `active`, or `archived`.
  3. Keep old versions available for audit replay.
- **Output**: Model registry.

## API Contract

```text
GET  /api/v1/learning/cases
GET  /api/v1/learning/cases/{case_id}
POST /api/v1/learning/backtest
GET  /api/v1/learning/backtest/{run_id}
POST /api/v1/learning/feedback
GET  /api/v1/learning/models
POST /api/v1/learning/models/{model_id}/activate
```

## Phase 13 Validation

- [ ] Historical case library contains at least 5 curated cases or seeded examples.
- [ ] Backtest can replay at least one historical scenario.
- [ ] Backtest output includes lead time, false alarms, missed events, and calibration error.
- [ ] Analyst feedback is stored and linked to recommendation ID.
- [ ] Model versions are tracked and auditable.
- [ ] New model versions do not overwrite past scenario results.

---

# PHASE 14 - MULTI-COMMODITY PLATFORM EXPANSION

**Owner**: Mayur Raj

**Support**: Abhishek Choudhary, Ayush Kumar

**Duration**: Sprint 12+

**Prerequisite**: Phase 13 learning foundation started; crude-oil MVP stable

## Objectives

- Expand EnergyShield AI from crude oil to LNG, coal, fertilizer, and critical minerals.
- Reuse the same data ingestion, knowledge graph, risk scoring, scenario modelling, recommendation, and dashboard architecture.
- Add commodity-specific adapters rather than duplicating the platform.

## Target Commodities

| Commodity         | Why It Matters                                         | Key Risks to Model                                                                         |
| ----------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| LNG               | Energy security, power, city gas, fertilizer feedstock | Export terminal outage, shipping delay, spot price spike, regas terminal congestion        |
| Coal              | Power generation and industrial energy supply          | Port disruption, rail bottleneck, weather impact, export restrictions, quality mismatch    |
| Fertilizers       | Agriculture and food security                          | Natural gas feedstock shock, urea/DAP/MOP import disruption, seasonal demand surge         |
| Critical minerals | EVs, batteries, electronics, defense manufacturing     | Export controls, supplier concentration, geopolitical restrictions, processing bottlenecks |

## Deliverables

| File or Module                                                           | Owner    | Description                                                       |
| ------------------------------------------------------------------------ | -------- | ----------------------------------------------------------------- |
| `backend/models/commodity_schema.py`                                   | Mayur    | Generic commodity, grade, demand sector, and supply chain schemas |
| `backend/commodities/base_adapter.py`                                  | Mayur    | Base adapter interface for all commodities                        |
| `backend/commodities/crude_oil_adapter.py`                             | Mayur    | Existing crude MVP adapter                                        |
| `backend/commodities/lng_adapter.py`                                   | Mayur    | LNG supply chain adapter                                          |
| `backend/commodities/coal_adapter.py`                                  | Mayur    | Coal supply chain adapter                                         |
| `backend/commodities/fertilizer_adapter.py`                            | Mayur    | Fertilizer supply chain adapter                                   |
| `backend/commodities/critical_minerals_adapter.py`                     | Mayur    | Critical minerals adapter                                         |
| `backend/scenarios/templates/lng_supply_shock.yaml`                    | Abhishek | LNG disruption scenario template                                  |
| `backend/scenarios/templates/coal_import_disruption.yaml`              | Abhishek | Coal disruption scenario template                                 |
| `backend/scenarios/templates/fertilizer_feedstock_shock.yaml`          | Abhishek | Fertilizer disruption scenario template                           |
| `backend/scenarios/templates/critical_mineral_export_restriction.yaml` | Abhishek | Critical mineral scenario template                                |
| `data/seeds/commodity_definitions.yaml`                                | Mayur    | Commodity-specific definitions and risk parameters                |
| `backend/api/routes/commodities.py`                                    | Ayush    | Commodity selection and commodity metadata APIs                   |
| `frontend/src/pages/CommodityCommandCenter.jsx`                        | Ayush    | Multi-commodity dashboard UI                                      |
| `frontend/src/components/commodities/CommoditySelector.jsx`            | Ayush    | Commodity selection component                                     |
| `docs/MULTI_COMMODITY_ROADMAP.md`                                      | Mayur    | Commodity-by-commodity expansion plan                             |

## Commodity Adapter Interface

```python
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
```

## Sequence

### 14.1 Generic Commodity Model

- **Priority**: P1
- **Task**: Generalize crude-oil schemas into commodity-agnostic schemas.
- **Input**: Existing crude entities and scenario outputs.
- **Processing**:
  1. Replace crude-only fields with generic commodity fields.
  2. Add commodity-specific grade/quality parameters.
  3. Add demand sector relationships.
- **Output**: Generic commodity schema.

### 14.2 Adapter Framework

- **Priority**: P1
- **Task**: Implement `CommodityAdapter` base class.
- **Input**: Commodity definitions.
- **Processing**:
  1. Define required methods.
  2. Create crude-oil adapter from existing MVP logic.
  3. Add tests to ensure adapters return consistent shapes.
- **Output**: Adapter framework.

### 14.3 LNG Adapter

- **Priority**: P2
- **Task**: Add LNG supply chain model.
- **Entities**:
  - LNG supplier country
  - Liquefaction/export terminal
  - LNG vessel route
  - Chokepoint
  - Regasification terminal
  - Demand sector: power, city gas, fertilizer
- **Scenarios**:
  - LNG export terminal outage
  - LNG spot price spike
  - Regas terminal congestion
  - Shipping route disruption
- **Output**: LNG risk and scenario support.

### 14.4 Coal Adapter

- **Priority**: P2
- **Task**: Add coal supply chain model.
- **Entities**:
  - Coal supplier country
  - Export port
  - Shipping route
  - Indian import port
  - Rail corridor
  - Power plant or industrial demand node
  - Coal grade/quality
- **Scenarios**:
  - Coal port disruption
  - Export restriction
  - Weather disruption
  - Rail bottleneck
- **Output**: Coal risk and scenario support.

### 14.5 Fertilizer Adapter

- **Priority**: P2
- **Task**: Add fertilizer supply chain model.
- **Entities**:
  - Fertilizer type: urea, DAP, MOP, ammonia
  - Feedstock: natural gas, ammonia, phosphates, potash
  - Supplier country
  - Export port
  - Indian import port
  - Domestic distribution node
  - Agricultural demand season
- **Scenarios**:
  - Natural gas feedstock shock
  - Urea import disruption
  - Potash export restriction
  - Seasonal demand surge
- **Output**: Fertilizer risk and scenario support.

### 14.6 Critical Minerals Adapter

- **Priority**: P2
- **Task**: Add critical minerals model.
- **Entities**:
  - Mineral: lithium, cobalt, nickel, graphite, rare earths
  - Mining country
  - Processing country
  - Export port
  - Manufacturing demand node
  - Dependency sector: EV, battery, electronics, defense
- **Scenarios**:
  - Export restriction
  - Processing bottleneck
  - Supplier concentration risk
  - Sanctions or geopolitical escalation
- **Output**: Critical mineral risk and scenario support.

### 14.7 Cross-Commodity Cascade Engine

- **Priority**: P3
- **Task**: Model how one commodity shock affects another.
- **Examples**:
  - LNG price spike increases fertilizer production cost.
  - Coal import disruption increases power sector stress.
  - Critical mineral export restriction affects EV manufacturing.
  - Crude oil disruption increases transport and logistics costs across commodities.
- **Output**: Cross-commodity scenario impact view.

### 14.8 Frontend Commodity Command Center

- **Priority**: P2
- **Task**: Add commodity selector and commodity-specific dashboards.
- **Input**: Commodity APIs.
- **Processing**:
  1. Select commodity.
  2. Load relevant map, risk cards, scenarios, and recommendations.
  3. Show commodity-specific assumptions.
- **Output**: Multi-commodity UI.

## API Contract

```text
GET  /api/v1/commodities
GET  /api/v1/commodities/{commodity_type}/entities
GET  /api/v1/commodities/{commodity_type}/risk
GET  /api/v1/commodities/{commodity_type}/scenarios
POST /api/v1/commodities/{commodity_type}/scenarios/run
GET  /api/v1/commodities/{commodity_type}/recommendations/{scenario_id}
```

## Phase 14 Validation

- [ ] Crude-oil MVP still works after adapter abstraction.
- [ ] At least one non-crude commodity can load entities and risk cards.
- [ ] LNG, coal, fertilizer, and critical minerals each have at least one scenario template.
- [ ] Knowledge graph supports commodity-specific nodes and relationships.
- [ ] Frontend can switch commodity without changing route structure.
- [ ] Cross-commodity cascade logic is documented, even if initially heuristic.

---

# PHASE 15 - FINAL PRESENTATION, DOCUMENTATION, AND RESUME PACKAGING

**Owner**: Ayush Kumar

**Support**: Abhishek Choudhary, Mayur Raj

**Duration**: Final sprint

**Prerequisite**: Phase 12 complete for MVP demo; Phases 13-14 can be roadmap or partial implementation

## Objectives

- Package the project as a polished long-term platform.
- Prepare demo video, presentation deck, architecture diagram, README, and resume points.
- Clearly separate MVP implemented features from future roadmap features.

## Deliverables

| File or Module                      | Owner    | Description                                                |
| ----------------------------------- | -------- | ---------------------------------------------------------- |
| `docs/DEMO_SCRIPT.md`             | Ayush    | 3-5 minute demo script                                     |
| `docs/ARCHITECTURE.md`            | Ayush    | Final architecture and component diagram                   |
| `docs/DATA_SOURCE_PLAN.md`        | Mayur    | Free and paid data source strategy                         |
| `docs/SCENARIO_ASSUMPTIONS.md`    | Abhishek | Scenario assumptions and limitations                       |
| `docs/CONTINUOUS_LEARNING.md`     | Abhishek | Learning roadmap and model governance                      |
| `docs/MULTI_COMMODITY_ROADMAP.md` | Mayur    | Expansion path to LNG, coal, fertilizer, critical minerals |
| `README.md`                       | Ayush    | Final public project documentation                         |
| `presentation/`                   | All      | Slides, screenshots, and demo assets                       |

## Resume-Ready Description

```text
EnergyShield AI - AI-Driven Energy Supply Chain Resilience Platform
Built a geospatial AI platform that ingests geopolitical news, maritime alerts, sanctions, commodity prices, and shipping signals to detect crude-oil disruption risks, model scenario impacts on import-dependent economies, and recommend alternate procurement routes and strategic reserve actions. Designed a knowledge graph linking suppliers, routes, chokepoints, ports, refineries, risks, and recommendations, with roadmap support for continuous learning and expansion into LNG, coal, fertilizers, and critical minerals.
```

## Phase 15 Validation

- [ ] Demo flow is stable and repeatable.
- [ ] Architecture diagram matches actual implementation.
- [ ] README setup instructions work.
- [ ] MVP vs future roadmap is clearly labelled.
- [ ] Resume bullets accurately reflect built features.

---

## MVP Build Order From Today

If the team starts implementation immediately, build in this order:

1. Phase 0 - Foundation and API schema freeze
2. Phase 1 - Data ingestion foundation
3. Phase 2 - Digital twin seed data and map layer
4. Phase 3 - Knowledge graph foundation
5. Phase 4 - Event extraction agent
6. Phase 5 - Risk scoring engine
7. Phase 6 - Scenario modeller
8. Phase 7 - Procurement and SPR recommendation agents
9. Phase 8 - Backend APIs and persistence
10. Phase 9 - Frontend dashboard with mock-to-live switching
11. Phase 10 - End-to-end orchestration
12. Phase 11 - Evaluation and audit trail
13. Phase 12 - Deployment and demo
14. Phase 13 - Continuous learning
15. Phase 14 - Multi-commodity expansion
16. Phase 15 - Presentation and documentation

---

## Responsibility Matrix

| Area                              | Primary Owner      | Secondary Support               |
| --------------------------------- | ------------------ | ------------------------------- |
| Frontend dashboard                | Ayush Kumar        | Mayur Raj, Abhishek Choudhary   |
| Backend APIs                      | Ayush Kumar        | Mayur Raj                       |
| Database and persistence          | Ayush Kumar        | Mayur Raj                       |
| Data source registry              | Mayur Raj          | Ayush Kumar                     |
| Data collectors                   | Mayur Raj          | Abhishek Choudhary              |
| Data orchestration                | Mayur Raj          | Ayush Kumar                     |
| Digital twin seed data            | Mayur Raj          | Ayush Kumar                     |
| Knowledge graph schema            | Mayur Raj          | Abhishek Choudhary              |
| Knowledge graph queries           | Mayur Raj          | Ayush Kumar                     |
| Event extraction agent            | Abhishek Choudhary | Mayur Raj                       |
| Entity resolution                 | Abhishek Choudhary | Mayur Raj                       |
| Risk scoring model                | Abhishek Choudhary | Mayur Raj                       |
| Scenario simulation               | Abhishek Choudhary | Mayur Raj                       |
| Procurement recommendation        | Mayur Raj          | Abhishek Choudhary              |
| SPR optimization                  | Abhishek Choudhary | Mayur Raj                       |
| End-to-end workflow orchestration | Mayur Raj          | Ayush Kumar, Abhishek Choudhary |
| Explainability and evaluation     | Abhishek Choudhary | Ayush Kumar                     |
| Continuous learning               | Abhishek Choudhary | Mayur Raj                       |
| Multi-commodity adapters          | Mayur Raj          | Abhishek Choudhary, Ayush Kumar |
| Deployment                        | Ayush Kumar        | Mayur Raj                       |
| Demo and presentation             | Ayush Kumar        | Abhishek Choudhary, Mayur Raj   |

---

## Dependency Graph Summary

```text
Phase 0 -> Phase 1
Phase 0 -> Phase 8
Phase 0 -> Phase 9
Phase 1 -> Phase 2
Phase 2 -> Phase 3
Phase 1 + Phase 3 -> Phase 4
Phase 3 + Phase 4 -> Phase 5
Phase 3 + Phase 5 -> Phase 6
Phase 3 + Phase 6 -> Phase 7
Phase 4 + Phase 5 + Phase 6 + Phase 7 + Phase 8 -> Phase 10
Phase 8 + Phase 9 + Phase 10 -> Phase 11
Phase 11 -> Phase 12
Phase 12 -> Phase 13
Phase 13 -> Phase 14
Phase 12 + Phase 13 + Phase 14 -> Phase 15
```

---

## Risk Register

| Risk                                                  | Impact                         | Mitigation                                                                            |
| ----------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------- |
| Real-time news changes too quickly                    | False alarms or missed signals | Use source reliability, corroboration, freshness, and official alerts where available |
| Free AIS coverage is incomplete                       | Weak vessel-level evidence     | Use AISStream/sample AIS for demo and PortWatch/seeded trends for stability           |
| Exact cargo and refinery contract data is unavailable | Scenario uncertainty           | Mark such fields as simulated and use transparent assumptions                         |
| Knowledge graph becomes overcomplicated               | Slow implementation            | Start with 10-12 node types and only core relationships                               |
| LLM extraction produces invalid JSON                  | Pipeline failures              | Validate output with Pydantic and add deterministic fallback rules                    |
| Risk scoring feels arbitrary                          | Low judge/user trust           | Show formula, top drivers, evidence, and calibration roadmap                          |
| Scenario assumptions are challenged                   | Credibility risk               | Store every assumption in`docs/SCENARIO_ASSUMPTIONS.md` and expose in UI            |
| Recommendation seems non-executable                   | Weak business impact           | Include cost, delay, risk, feasibility, confidence, and constraints for every option  |
| Continuous learning overfits small historical data    | Misleading improvement claims  | Use backtesting, model registry, and conservative deployment gates                    |
| Multi-commodity expansion breaks crude MVP            | Regression risk                | Add adapter interface and tests before adding new commodities                         |
| Team members overlap on same files                    | Merge conflicts                | Assign file ownership by phase and freeze schemas before parallel work                |

---

## Definition of Done for MVP

The MVP is complete when the following end-to-end pipeline works:

```text
Seeded or live source signal
  -> normalized data record
  -> structured risk event
  -> graph-linked affected entities
  -> corridor/supplier risk score update
  -> triggered scenario simulation
  -> procurement and SPR recommendation
  -> dashboard visualization
  -> executive report
  -> audit trail
```

Minimum required demo capabilities:

- [ ] Dashboard with current risks
- [ ] Digital twin map
- [ ] Knowledge graph relationship query
- [ ] Latest events feed
- [ ] Corridor and supplier risk scores
- [ ] Scenario simulator with at least 3 scenarios
- [ ] Procurement recommendation table
- [ ] SPR recommendation panel
- [ ] Explainability panel
- [ ] Report generation
- [ ] Audit trail

---

## Long-Term Extension Summary

After MVP, prioritize these features:

1. **Knowledge Graph Depth**

   - Add company-level suppliers, vessel operators, banks, insurers, and contract placeholders.
   - Improve refinery-grade compatibility logic.
   - Add graph path explanations in recommendations.
2. **Continuous Learning**

   - Add historical disruption case library.
   - Backtest risk thresholds.
   - Calibrate event severity and recommendation scoring.
   - Capture human feedback on accepted/rejected recommendations.
3. **Multi-Commodity Expansion**

   - Convert crude-specific logic into adapter-based commodity modules.
   - Add LNG first, then coal, fertilizer, and critical minerals.
   - Add cross-commodity cascade modelling.

---

_Implementation Plan v1.0 - EnergyShield AI_

_Last Updated: July 06, 2026_
