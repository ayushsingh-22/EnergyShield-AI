"""Reads AIS stream or sample AIS records for chokepoint monitoring (Phase 1)."""

from __future__ import annotations

import logging
import os
from typing import Any, List
from datetime import datetime, timezone

from ingestion.base_collector import BaseCollector
from ingestion.http_client import fetch_json
from ingestion.source_registry import get_source_reliability
from models.data_source_schema import RawSourceRecord

logger = logging.getLogger(__name__)

# AISHub webservice - free for data-sharing members; authenticates by
# `username` (not an API key) and is hard rate-limited to one request per
# minute. We poll a bounding box around a monitored chokepoint and summarise
# vessel activity into a single signal. See https://www.aishub.net/api
_AISHUB_URL = os.getenv("AISHUB_URL", "https://data.aishub.net/ws.php")
_AISHUB_USERNAME = os.getenv("AISHUB_USERNAME", "")
_LIVE_FEEDS_ENABLED = os.getenv("ENABLE_LIVE_FEEDS", "false").lower() in ("1", "true", "yes")

# Bounding box around the Strait of Hormuz (lat 24-27 N, lon 54-58 E) - the
# highest-value chokepoint for this app. AISHub's free tier covers member
# coverage areas; an empty result simply falls back to seeded data.
_HORMUZ_BBOX = {"latmin": 24.0, "latmax": 27.5, "lonmin": 54.0, "lonmax": 58.5}


class AisCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="ais_stream")
        self.reliability = get_source_reliability(self.source_name)

    def _seeded(self) -> List[dict]:
        return [
            {
                "title": "AIS Stream: Vessel Rerouting Detected",
                "summary": "Multiple VLCCs have altered course away from the Red Sea.",
                "url": "https://example.com/ais/rerouting",
                "language": "en",
                "location_name": "Red Sea",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

    def _fetch_live(self) -> List[dict] | None:
        """Polls AISHub for vessels around the Strait of Hormuz and
        summarises count + average speed into one signal; None on failure."""
        if not _AISHUB_USERNAME:
            return None
        payload = fetch_json(
            _AISHUB_URL,
            params={
                "username": _AISHUB_USERNAME,
                "format": 1,  # human-readable
                "output": "json",
                "compress": 0,
                **_HORMUZ_BBOX,
            },
            source_name=self.source_name,
            timeout=15.0,
        )
        # AISHub returns [ {metadata...}, [ {vessel}, ... ] ] on success, or a
        # metadata-only error object when rate-limited / no data.
        vessels: list = []
        if isinstance(payload, list) and len(payload) >= 2 and isinstance(payload[1], list):
            vessels = payload[1]
        if not vessels:
            return None

        moving = [v for v in vessels if isinstance(v.get("SOG"), (int, float)) and 0 < v["SOG"] < 102.4]
        avg_speed = round(sum(v["SOG"] for v in moving) / len(moving), 1) if moving else 0.0
        return [
            {
                "title": "AIS: Strait of Hormuz vessel activity",
                "summary": (
                    f"AISHub reports {len(vessels)} vessels in the Strait of Hormuz box "
                    f"({len(moving)} under way, avg speed {avg_speed} kn)."
                ),
                "url": "https://www.aishub.net/",
                "language": "en",
                "location_name": "Strait of Hormuz",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

    def fetch(self) -> List[RawSourceRecord]:
        try:
            data = self._fetch_live() if _LIVE_FEEDS_ENABLED else None
            if data is None:
                data = self._seeded()
            return self.normalize(data)
        except Exception as e:
            logger.error(f"Error fetching from {self.source_name}: {e}")
            return []

    def normalize(self, raw_data: Any) -> List[RawSourceRecord]:
        records = []
        for item in raw_data:
            try:
                published_at_str = item.get("published_at")
                published_at = datetime.fromisoformat(published_at_str) if published_at_str else None

                record = RawSourceRecord(
                    source_name=self.source_name,
                    reliability_tier=self.reliability,
                    published_at=published_at,
                    detected_at=datetime.now(timezone.utc),
                    title=item.get("title"),
                    raw_text=item.get("summary", ""),
                    url=item.get("url"),
                    language=item.get("language"),
                    location_name=item.get("location_name")
                )
                records.append(record)
            except Exception as e:
                logger.warning(f"Failed to normalize record in {self.source_name}: {e}")
        return records

    def health(self) -> bool:
        return True
