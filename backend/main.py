"""FastAPI application entry point.

Routers register here as each `backend/api/routes/*.py` module is
implemented (see docs/API_REFERENCE.md for the frozen contract).
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env (API keys for live data feeds, DB creds, etc.) before any module
# reads os.getenv at import time. Searches upward from cwd, so it finds the
# repo-root .env whether the app is started from backend/ or the repo root.
load_dotenv()

from api.routes import (
    audit,
    commodities,
    data_sources,
    digital_twin,
    events,
    graph,
    health,
    learning,
    recommendations,
    reports,
    risk,
    scenarios,
)
from db.init_db import init_db
from orchestration.scheduler import configure_default_jobs

logger = logging.getLogger(__name__)

API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Best-effort: creates persistence tables when Postgres is reachable.
    # A missing/unreachable database must never prevent the API from
    # serving requests from in-memory service state (see `db/init_db.py`).
    if not init_db():
        logger.info("Starting with in-memory service state only; Postgres was not reachable at startup.")

    # Starts the Phase 10 background scheduler (data refresh -> event
    # extraction -> risk/graph update -> scenario auto-trigger ->
    # recommendation generation, per `DATA_REFRESH_INTERVAL_MINUTES`).
    scheduler = configure_default_jobs()
    scheduler.start()

    yield

    scheduler.stop()


app = FastAPI(
    title="EnergyShield AI",
    description="AI-driven energy supply chain resilience platform.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=API_V1_PREFIX)
app.include_router(data_sources.router)
app.include_router(digital_twin.router)
app.include_router(graph.router)
app.include_router(events.router)
app.include_router(risk.router)
app.include_router(scenarios.router)
app.include_router(recommendations.router)
app.include_router(reports.router)
app.include_router(commodities.router)
app.include_router(audit.router)
app.include_router(learning.router)
