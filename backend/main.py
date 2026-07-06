"""FastAPI application entry point.

Only the health route is wired in during Phase 0. Later phases register
their routers here as each `backend/api/routes/*.py` module is implemented
(see docs/API_REFERENCE.md for the frozen contract).
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health

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
