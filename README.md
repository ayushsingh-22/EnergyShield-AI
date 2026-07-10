# EnergyShield AI

AI-driven energy supply chain resilience platform for import-dependent
economies. Turns fast-changing geopolitical, maritime, sanctions, commodity,
and logistics signals into structured risk events, corridor and supplier
risk scores, disruption scenario simulations, procurement rerouting
recommendations, and strategic reserve action plans.

**MVP focus:** India's crude-oil import disruption resilience. The data
model, knowledge graph, and pipeline are commodity-agnostic so LNG, coal,
fertilizer, and critical minerals can be added later through adapters
(see `ENERGYSHIELD_IMPLEMENTATION_PLAN.md`, Phase 14).

## Status

Repository foundation (Phase 0). Core Pydantic schemas, the API contract,
and the local dev stack are in place; most `backend/` and `frontend/`
modules are placeholder stubs to be filled in phase by phase per
[`ENERGYSHIELD_IMPLEMENTATION_PLAN.md`](./ENERGYSHIELD_IMPLEMENTATION_PLAN.md).

## Architecture

See [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) for the full component
diagram. In short:

```text
data sources -> ingestion -> event extraction agent -> knowledge graph
  -> risk scoring -> scenario modeller -> procurement/SPR agents
  -> backend API + audit trail -> React dashboard
```

## Repository Layout

```text
backend/   FastAPI app: api, agents, commodities, db, evaluation, graph,
           ingestion, learning, models, optimization, orchestration,
           reports, risk, scenarios, services, tests
frontend/  Vite + React analyst dashboard
data/      Seed CSV/GeoJSON/YAML for the digital twin and demo cases
docs/      Architecture, API contract, data source plan, scenario
           assumptions, continuous learning, multi-commodity roadmap
```

## Quick Start

### Option A: Docker Compose (full stack)

```bash
cp .env.example .env
docker-compose up --build
```

- Backend: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- Backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Frontend: [http://localhost:5173](http://localhost:5173)

### Option B: Run services locally

Backend (requires [Poetry](https://python-poetry.org/); if `poetry` isn't on
your `PATH` after `pip install poetry`, substitute `python -m poetry` for
`poetry` below):

```bash
cd backend
poetry install
poetry run uvicorn main:app --reload
```

- Health check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Frontend:

```bash
cd frontend
npm install
npm run dev
```

- App: [http://localhost:5173](http://localhost:5173)

Run backend and frontend in separate terminals - both need to stay running
for the dashboard to reach the live API (or set
`VITE_USE_MOCK_DATA=true` in `frontend/.env.local` to work on the UI without
the backend running).

By default the frontend targets `VITE_USE_MOCK_DATA=true` (see
`frontend/.env.example`), so UI work can proceed against
`frontend/src/api/mockData.js` before every backend endpoint is live.

## Team Ownership

| Role                                          | Person             | Core Responsibility                                                                     |
| --------------------------------------------- | ------------------ | --------------------------------------------------------------------------------------- |
| Frontend and Backend Lead                     | Ayush Kumar        | Frontend dashboard, backend APIs, database integration, report generation, deployment   |
| ML and Agents Lead                            | Abhishek Choudhary | Event extraction, risk scoring, scenario modelling, continuous learning, explainability |
| Data, Orchestration, and Knowledge Graph Lead | Mayur Raj          | Data ingestion, schedulers, orchestration, knowledge graph, procurement orchestration   |

## Non-Negotiable Product Decisions

1. Long-term decision-support platform, not a one-time hackathon dashboard.
2. Crude oil first for India, but the data model stays commodity-agnostic.
3. Real-time news is unreliable until validated by multiple sources.
4. Every signal stores source, timestamp, freshness, reliability, confidence,
   and evidence URL.
5. Every recommendation shows assumptions and explains why it was generated.
6. A knowledge graph is the relationship layer between suppliers, routes,
   chokepoints, ports, refineries, risks, scenarios, and recommendations.
7. Continuous learning improves model weights using historical disruptions,
   backtests, and human feedback.
8. Multi-commodity expansion reuses the platform through adapters, not
   separate codebases.
9. Simulated values (refinery contracts, exact cargo details, tanker
   availability, crude-grade compatibility) are always marked as such.
10. Interfaces are frozen through Pydantic schemas (`backend/models/`) so
    frontend, backend, ML, and orchestration work can run in parallel.

Full detail, phase-by-phase deliverables, and validation checklists live in
[`ENERGYSHIELD_IMPLEMENTATION_PLAN.md`](./ENERGYSHIELD_IMPLEMENTATION_PLAN.md).
