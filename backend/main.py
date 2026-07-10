"""FastAPI application entry point.

Routers register here as each `backend/api/routes/*.py` module is
implemented (see docs/API_REFERENCE.md for the frozen contract).
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import (
    commodities,
    data_sources,
    digital_twin,
    events,
    graph,
    health,
    recommendations,
    reports,
    risk,
    scenarios,
)

API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(
    title="EnergyShield AI",
    description="AI-driven energy supply chain resilience platform.",
    version="0.1.0",
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
