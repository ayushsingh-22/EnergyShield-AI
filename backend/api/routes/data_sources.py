"""Data freshness and source health endpoints (Phase 1 ingestion foundation).

See docs/API_REFERENCE.md for the endpoints this router will own.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/data", tags=["data-sources"])

# TODO(Phase 1): implement endpoints listed in docs/API_REFERENCE.md
