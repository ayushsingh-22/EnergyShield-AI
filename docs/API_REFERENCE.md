# EnergyShield AI - API Reference

Frozen API contract for the crude-oil MVP (Planning Principle #10). Frontend,
backend, ML, and orchestration work can proceed in parallel against this
contract even before every endpoint is implemented. All request/response
bodies are Pydantic models defined under `backend/models/`.

Base path: `{API_V1_PREFIX}` (default `/api/v1`, see `.env.example`).

Status legend: **Live** = implemented and wired into `backend/main.py`.
**Planned** = contract frozen, implementation lands in the noted phase.

## Health and Data Freshness

| Method | Path | Status | Response Schema | Notes |
| --- | --- | --- | --- | --- |
| GET | `/health` | Live (Phase 0) | `health.HealthStatus` | Liveness check |
| GET | `/data/freshness` | Live (Phase 1) | `data_source_schema.SourceFreshness[]` | Per-source last-fetch time and health |

## Events

| Method | Path | Status | Response Schema | Notes |
| --- | --- | --- | --- | --- |
| GET | `/events/latest` | Live (Phase 4) | `event_schema.RiskEvent[]` | Latest structured events, most recent first; `?limit=` (default 50, max 200) |
| GET | `/events/{event_id}` | Live (Phase 4) | `event_schema.RiskEvent` | Single event detail; 404 if unknown |

## Risk

| Method | Path | Status | Response Schema | Notes |
| --- | --- | --- | --- | --- |
| GET | `/risk/corridors` | Live (Phase 5 demo) | risk score list | Chokepoint/route risk cards |
| GET | `/risk/suppliers` | Live (Phase 5 demo) | risk score list | Supplier country/company risk cards |
| GET | `/risk/history/{entity_id}` | Live (Phase 5 demo) | risk score history | Trend data for charts |

## Digital Twin

| Method | Path | Status | Response Schema | Notes |
| --- | --- | --- | --- | --- |
| GET | `/digital-twin/map` | Live (Phase 2) | map layer bundle | Suppliers, routes, chokepoints, ports, refineries, SPR sites |
| GET | `/digital-twin/suppliers` | Live (Phase 2) | supplier list | |
| GET | `/digital-twin/routes` | Live (Phase 2) | route list | |
| GET | `/digital-twin/chokepoints` | Live (Phase 2) | chokepoint list | |
| GET | `/digital-twin/refineries` | Live (Phase 2) | refinery list | |
| GET | `/digital-twin/exposure` | Live (Phase 2) | exposure baseline | |

## Knowledge Graph

| Method | Path | Status | Response Schema | Notes |
| --- | --- | --- | --- | --- |
| GET | `/graph/entity/{entity_id}` | Live (Phase 3) | `graph_schema.GraphQueryResult` | Node + direct relationships; 404 if entity not seeded |
| GET | `/graph/refineries-exposed?chokepoint_id=` | Live (Phase 3) | refinery list | |
| GET | `/graph/alternative-suppliers?supplier_id=&commodity=` | Live (Phase 3) | supplier list | Excludes suppliers with an active (non-expired) AFFECTS edge |
| GET | `/graph/routes?supplier_id=` | Live (Phase 3) | route list | |
| POST | `/graph/query-impact` | Live (Phase 3) | `graph_schema.GraphQueryResult` | Body: `graph_schema.ImpactQueryRequest` (`entity_id`, `max_hops` 1-5) |

## Scenarios

| Method | Path | Status | Request Schema | Response Schema | Notes |
| --- | --- | --- | --- | --- | --- |
| POST | `/scenarios/run` | Live (Phase 6 demo) | `scenario_schema.ScenarioRequest` | `scenario_schema.ScenarioResult` | Deterministic demo simulation |
| GET | `/scenarios/{scenario_id}` | Live (Phase 6 demo) | - | `scenario_schema.ScenarioResult` | In-memory scenario retrieval |

## Recommendations

| Method | Path | Status | Response Schema | Notes |
| --- | --- | --- | --- | --- |
| GET | `/recommendations/{scenario_id}` | Live (Phase 7 demo) | `recommendation_schema.Recommendation` | Generated from stored scenario output |

## Reports and Audit

| Method | Path | Status | Notes |
| --- | --- | --- | --- |
| POST | `/reports/generate` | Live (Phase 8 demo) | Executive crisis-response report |
| GET | `/audit/{entity_id}` | Planned (Phase 11) | Full audit trail for an event/scenario/recommendation |

## Continuous Learning

| Method | Path | Status | Notes |
| --- | --- | --- | --- |
| GET | `/learning/cases` | Planned (Phase 13) | Historical disruption case library |
| GET | `/learning/cases/{case_id}` | Planned (Phase 13) | |
| POST | `/learning/backtest` | Planned (Phase 13) | |
| GET | `/learning/backtest/{run_id}` | Planned (Phase 13) | |
| POST | `/learning/feedback` | Planned (Phase 13) | |
| GET | `/learning/models` | Planned (Phase 13) | |
| POST | `/learning/models/{model_id}/activate` | Planned (Phase 13) | |

## Multi-Commodity

| Method | Path | Status | Notes |
| --- | --- | --- | --- |
| GET | `/commodities` | Live (Phase 14 partial) | |
| GET | `/commodities/{commodity_type}/entities` | Live (Phase 14 partial) | |
| GET | `/commodities/{commodity_type}/risk` | Live (Phase 14 partial) | |
| GET | `/commodities/{commodity_type}/scenarios` | Live (Phase 14 partial) | |
| POST | `/commodities/{commodity_type}/scenarios/run` | Live (Phase 14 partial) | |
| GET | `/commodities/{commodity_type}/recommendations/{scenario_id}` | Live (Phase 14 partial) | |

## Conventions

- Every response uses the shared enums in `backend/models/core_schema.py`
  (`CommodityType`, `RiskEventType`, `RiskLevel`, `SourceReliability`) - do
  not introduce parallel string literals in route handlers.
- Any endpoint returning a derived output (risk score, scenario, recommendation)
  must include `confidence` and `assumptions` per `core_schema.AuditableMixin`.
- Simulated data always carries `is_simulated: true`; never omit the field
  to make demo data look real.
- Breaking changes to a **Live** endpoint require updating this file and the
  frontend mock data (`frontend/src/api/mockData.js`) in the same change.

