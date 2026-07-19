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
| POST | `/scenarios/run` | Live (Phase 6) | `scenario_schema.ScenarioRequest` | `scenario_schema.ScenarioResult` | Runs `scenarios/scenario_engine.py` against YAML templates + graph/digital-twin-derived refinery exposure |
| GET | `/scenarios/{scenario_id}` | Live (Phase 6) | - | `scenario_schema.ScenarioResult` | In-memory scenario retrieval |

## Recommendations

| Method | Path | Status | Response Schema | Notes |
| --- | --- | --- | --- | --- |
| GET | `/recommendations/{scenario_id}` | Live (Phase 7) | `recommendation_schema.Recommendation` | Procurement options ranked via `optimization/procurement_optimizer.py`; SPR plan via `optimization/spr_optimizer.py` |

## Reports and Audit

| Method | Path | Status | Notes |
| --- | --- | --- | --- |
| POST | `/reports/generate` | Live (Phase 8) | Executive crisis-response report, includes a rendered Markdown brief |
| GET | `/audit/{entity_id}` | Live (Phase 8 / Phase 11) | Full audit trail for an event/scenario/recommendation/report |

## Continuous Learning

| Method | Path | Status | Notes |
| --- | --- | --- | --- |
| GET | `/learning/cases` | Live (Phase 13) | Historical disruption case library, seeded from `data/seeds/demo_disruption_cases.json` |
| GET | `/learning/cases/{case_id}` | Live (Phase 13) | |
| POST | `/learning/backtest` | Live (Phase 13) | Replays cases through the current scenario engine; body: `case_ids?`, `flag_threshold_percent` |
| GET | `/learning/backtest/{run_id}` | Live (Phase 13) | |
| POST | `/learning/feedback` | Live (Phase 13) | |
| GET | `/learning/models` | Live (Phase 13) | |
| POST | `/learning/models/{model_id}/activate` | Live (Phase 13) | |

## Multi-Commodity

| Method | Path | Status | Notes |
| --- | --- | --- | --- |
| GET | `/commodities` | Live (Phase 14) | |
| GET | `/commodities/{commodity_type}/entities` | Live (Phase 14) | Delegates to each commodity's `CommodityAdapter`; non-crude entities are illustrative/simulated |
| GET | `/commodities/{commodity_type}/risk` | Live (Phase 14 partial) | Crude oil uses live risk scores; other commodities return a placeholder pending live ingestion |
| GET | `/commodities/{commodity_type}/scenarios` | Live (Phase 14) | |
| POST | `/commodities/{commodity_type}/scenarios/run` | Live (Phase 14) | |
| GET | `/commodities/{commodity_type}/recommendations/{scenario_id}` | Live (Phase 14) | |

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

