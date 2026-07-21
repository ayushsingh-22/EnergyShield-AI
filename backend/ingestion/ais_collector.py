"""Reads AIS stream or sample AIS records for chokepoint monitoring (Phase 1)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, List
from datetime import datetime, timezone

from ingestion.base_collector import BaseCollector
from ingestion.http_client import fetch_json
from ingestion.source_registry import get_source_reliability
from models.data_source_schema import RawSourceRecord

logger = logging.getLogger(__name__)

_LIVE_FEEDS_ENABLED = os.getenv("ENABLE_LIVE_FEEDS", "false").lower() in ("1", "true", "yes")

# --- Provider config ------------------------------------------------------
# AISStream.io (primary): free, instant API key at https://aisstream.io. It's
# a WebSocket push stream, so we connect, collect PositionReports inside the
# monitored box for a few seconds, then disconnect and summarise.
_AISSTREAM_URL = os.getenv("AISSTREAM_URL", "wss://stream.aisstream.io/v0/stream")
_AISSTREAM_API_KEY = os.getenv("AISSTREAM_API_KEY", "")
_AISSTREAM_COLLECT_SECONDS = float(os.getenv("AISSTREAM_COLLECT_SECONDS", "6"))

# AISHub (secondary): free for data-sharing members; authenticates by
# `username` (not an API key), hard-limited to one request per minute.
# See https://www.aishub.net/api
_AISHUB_URL = os.getenv("AISHUB_URL", "https://data.aishub.net/ws.php")
_AISHUB_USERNAME = os.getenv("AISHUB_USERNAME", "")

# Bounding box around the Strait of Hormuz (lat 24-27.5 N, lon 54-58.5 E) -
# the highest-value chokepoint for this app.
_HORMUZ_BBOX = {"latmin": 24.0, "latmax": 27.5, "lonmin": 54.0, "lonmax": 58.5}
# AISStream expects boxes as [[[lat,lon],[lat,lon]]] (SW then NE corner).
_HORMUZ_BBOX_AISSTREAM = [[[24.0, 54.0], [27.5, 58.5]]]


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

    def _signal(self, provider: str, vessel_count: int, moving: int, avg_speed: float) -> List[dict]:
        return [
            {
                "title": "AIS: Strait of Hormuz vessel activity",
                "summary": (
                    f"{provider} reports {vessel_count} vessels in the Strait of Hormuz box "
                    f"({moving} under way, avg speed {avg_speed} kn)."
                ),
                "url": "https://aisstream.io/" if provider == "AISStream" else "https://www.aishub.net/",
                "language": "en",
                "location_name": "Strait of Hormuz",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

    async def _collect_aisstream(self) -> List[dict]:
        """Connects to AISStream.io, collects PositionReports inside the
        Hormuz box for a few seconds, then disconnects. Raises on any
        failure so the caller can fall through to the next provider."""
        import websockets  # local import: only needed on the live path

        vessels: dict[int, dict] = {}
        async with websockets.connect(_AISSTREAM_URL, open_timeout=10, close_timeout=5) as ws:
            await ws.send(json.dumps({
                "APIKey": _AISSTREAM_API_KEY,
                "BoundingBoxes": _HORMUZ_BBOX_AISSTREAM,
                "FilterMessageTypes": ["PositionReport"],
            }))
            try:
                async with asyncio.timeout(_AISSTREAM_COLLECT_SECONDS):
                    async for raw in ws:
                        message = json.loads(raw)
                        if message.get("MessageType") != "PositionReport":
                            continue
                        report = message.get("Message", {}).get("PositionReport", {})
                        meta = message.get("MetaData", {})
                        mmsi = meta.get("MMSI") or report.get("UserID")
                        if mmsi is None:
                            continue
                        vessels[int(mmsi)] = {"sog": report.get("Sog")}
            except (asyncio.TimeoutError, TimeoutError):
                pass  # collection window elapsed - expected

        moving = [v for v in vessels.values() if isinstance(v["sog"], (int, float)) and 0 < v["sog"] < 102.3]
        avg_speed = round(sum(v["sog"] for v in moving) / len(moving), 1) if moving else 0.0
        return self._signal("AISStream", len(vessels), len(moving), avg_speed)

    def _fetch_aisstream(self) -> List[dict] | None:
        if not _AISSTREAM_API_KEY:
            return None
        try:
            data = asyncio.run(self._collect_aisstream())
            return data or None
        except Exception as exc:  # noqa: BLE001 - external source, must not crash pipeline
            logger.info("Live fetch for 'ais_stream' (AISStream) failed (%s); trying next provider.", exc)
            return None

    def _fetch_aishub(self) -> List[dict] | None:
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
        # AISHub returns [ {metadata...}, [ {vessel}, ... ] ] on success.
        vessels: list = []
        if isinstance(payload, list) and len(payload) >= 2 and isinstance(payload[1], list):
            vessels = payload[1]
        if not vessels:
            return None
        moving = [v for v in vessels if isinstance(v.get("SOG"), (int, float)) and 0 < v["SOG"] < 102.4]
        avg_speed = round(sum(v["SOG"] for v in moving) / len(moving), 1) if moving else 0.0
        return self._signal("AISHub", len(vessels), len(moving), avg_speed)

    def _fetch_live(self) -> List[dict] | None:
        """Resolves a vessel-position provider by config: AISStream.io first
        (free, instant key), then AISHub (member username), else None to
        fall back to seeded data."""
        return self._fetch_aisstream() or self._fetch_aishub()

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
