"""FastAPI application entry point.

Routers register here as each `backend/api/routes/*.py` module is
implemented (see docs/API_REFERENCE.md for the frozen contract).
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import data_sources, digital_twin, graph, health

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
# These routers embed the full "/api/v1/..." prefix themselves.
app.include_router(data_sources.router)
app.include_router(digital_twin.router)
app.include_router(graph.router)
