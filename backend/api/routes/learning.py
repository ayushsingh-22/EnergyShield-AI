"""Historical case library, backtest, feedback, and model version endpoints
(Phase 13 continuous learning from past disruptions).

See docs/API_REFERENCE.md for the endpoints this router will own.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/learning", tags=["learning"])

# TODO(Phase 13): implement endpoints listed in docs/API_REFERENCE.md
