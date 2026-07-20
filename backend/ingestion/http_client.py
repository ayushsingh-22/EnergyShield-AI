"""Shared HTTP fetch helper for live data collectors (Phase 1).

Every collector that reads a real external feed goes through this so the
graceful-degradation contract is uniform: a network error, timeout, non-2xx
status, or malformed body returns `None`, and the caller falls back to its
seeded sample data instead of raising. Real feeds are opt-in per collector -
when the relevant URL/key isn't configured, the collector never calls here
at all and stays on seeded data.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Kept short so a slow/unreachable source degrades to seeded data quickly
# rather than stalling the whole ingestion pipeline run.
_DEFAULT_TIMEOUT_SECONDS = 8.0


def fetch_json(url: str, params: dict[str, Any] | None = None, *, source_name: str,
               timeout: float = _DEFAULT_TIMEOUT_SECONDS) -> Any | None:
    """GET `url` and return parsed JSON, or `None` on any failure.

    Never raises - a failed live fetch must not break the pipeline; the
    caller logs the fallback and uses seeded data instead.
    """
    try:
        response = httpx.get(url, params=params, timeout=timeout, follow_redirects=True,
                             headers={"User-Agent": "EnergyShield-AI/0.1 (ingestion)"})
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # noqa: BLE001 - external source, must not crash pipeline
        logger.info("Live fetch for '%s' failed (%s); falling back to seeded sample data.", source_name, exc)
        return None


def fetch_text(url: str, params: dict[str, Any] | None = None, *, source_name: str,
               timeout: float = _DEFAULT_TIMEOUT_SECONDS) -> str | None:
    """GET `url` and return the raw response text, or `None` on any failure."""
    try:
        response = httpx.get(url, params=params, timeout=timeout, follow_redirects=True,
                             headers={"User-Agent": "EnergyShield-AI/0.1 (ingestion)"})
        response.raise_for_status()
        return response.text
    except Exception as exc:  # noqa: BLE001 - external source, must not crash pipeline
        logger.info("Live fetch for '%s' failed (%s); falling back to seeded sample data.", source_name, exc)
        return None
