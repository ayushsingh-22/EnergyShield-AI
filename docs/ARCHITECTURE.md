# EnergyShield AI - Architecture

## System Overview

EnergyShield AI converts fast-changing geopolitical, maritime, sanctions,
commodity, and logistics signals into structured risk events, corridor and
supplier risk scores, disruption scenario simulations, procurement
rerouting recommendations, and strategic reserve action plans. The MVP
scope is India's crude-oil import disruption resilience; the architecture
is commodity-agnostic so LNG, coal, fertilizer, and critical minerals can be
added later through adapters (Phase 14) rather than new codebases.

## Component Diagram

```text
                        +---------------------+
                        |   Data Sources       |
                        | GDELT/RSS, UKMTO,    |
                        | OFAC, EIA/FRED, AIS, |
                        | PortWatch, PPAC CSV  |
                        +----------+-----------+
                                   |
                                   v
                     +-------------------------+
                     | backend/ingestion/      |
                     | collectors + normalizer |
                     +------------+------------+
                                   |  NormalizedSignal
                                   v
                     +-------------------------+
                     | backend/agents/          |
                     | event_extraction_agent   |
                     | entity_resolution_agent  |
                     +------------+------------+
                                   |  RiskEvent
                                   v
        +---------------------------------------------+
        |            backend/graph/ (Neo4j)             |
        |  suppliers - routes - chokepoints - refineries |
        |  - risk events - scenarios - recommendations   |
        +---------------------+-------------------------+
                                   |
                                   v
                     +-------------------------+
                     | backend/risk/            |
                     | risk_scoring_engine      |
                     +------------+------------+
                                   |  RiskScore
                                   v
                     +-------------------------+
                     | backend/scenarios/       |
                     | scenario_engine          |
                     +------------+------------+
                                   |  ScenarioResult
                                   v
                     +-------------------------+
                     | backend/optimization/    |
                     | backend/agents/          |
                     | procurement_agent, spr_agent |
                     +------------+------------+
                                   |  Recommendation
                                   v
        +---------------------------------------------+
        | backend/api/ (FastAPI) -> backend/db/ (Postgres)|
        | backend/services/audit_service (audit trail)    |
        +---------------------+-------------------------+
                                   |
                                   v
                     +-------------------------+
                     |   frontend/ (React)      |
                     |  Dashboard, Map, Risk,   |
                     |  Scenario, Recommendation|
                     +-------------------------+
```

`backend/orchestration/` (Phase 10) ties the pipeline together on a
schedule and via an event bus (Redis) so a new signal automatically
propagates through extraction, graph update, risk scoring, scenario
triggering, and recommendation generation without manual steps.

## Data Stores

| Store | Purpose | Owner module |
| --- | --- | --- |
| PostgreSQL | Relational persistence: raw records, normalized signals, risk events, risk scores, scenario runs, recommendations, audit events, reports | `backend/db/` |
| Neo4j | Knowledge graph: supplier-route-chokepoint-refinery-risk-scenario-recommendation relationships | `backend/graph/` |
| Redis | Event bus and job status for orchestration/scheduling | `backend/orchestration/` |

## Why a Knowledge Graph

Risk and recommendation questions in this domain are relationship-heavy
("which refineries are exposed to a Hormuz closure?", "which suppliers can
replace Iran for a compatible crude grade?"). Encoding suppliers, routes,
chokepoints, ports, refineries, and reserve sites as a graph (Phase 3) lets
the risk engine, scenario modeller, and procurement agent answer these with
graph traversals instead of hardcoded lookup tables, and lets that same
traversal logic generalize to new commodities in Phase 14.

## Design Principles Baked Into the Architecture

1. **Frozen schemas, parallel tracks.** `backend/models/*.py` schemas are
   the contract between frontend, backend, ML, and orchestration work
   (Planning Principle #10). Frontend development starts against
   `frontend/src/api/mockData.js` shaped to these schemas before the live
   API exists.
2. **Provenance everywhere.** Every signal, event, risk score, scenario, and
   recommendation embeds source, timestamp, reliability, confidence, and
   evidence (`core_schema.SourceMetadata`, `AuditableMixin`).
3. **Commodity-agnostic core.** Crude oil is the first `CommodityAdapter`
   implementation (Phase 14); the ingestion, graph, risk, scenario, and
   recommendation layers operate on generic commodity types, not
   crude-only fields.
4. **Deterministic fallback for every AI component.** The LLM-backed event
   extraction agent falls back to rule-based keyword extraction if the LLM
   call fails or returns invalid JSON, so the pipeline never silently drops
   a signal.
5. **Everything simulated is labelled.** Any field derived from placeholder
   or estimated data (exact cargo details, tanker availability, crude-grade
   compatibility) carries `is_simulated: true` end to end into the UI.

## Deployment

`docker-compose.yml` runs the full stack locally: `postgres`, `neo4j`,
`redis`, `backend` (FastAPI via Uvicorn, hot-reloaded), and `frontend`
(Vite dev server). See the root `README.md` for the quick-start commands.

## Repository Layout

See the "Recommended Repository Structure" section of
`ENERGYSHIELD_IMPLEMENTATION_PLAN.md` for the full file-by-file layout and
phase-by-phase ownership. At a glance:

```text
backend/   FastAPI app: api, agents, commodities, db, evaluation, graph,
           ingestion, learning, models, optimization, orchestration,
           reports, risk, scenarios, services, tests
frontend/  Vite + React dashboard
data/      Seed CSV/GeoJSON/YAML for the digital twin and demo cases
docs/      Architecture, API contract, data source plan, scenario
           assumptions, continuous learning, multi-commodity roadmap
```
