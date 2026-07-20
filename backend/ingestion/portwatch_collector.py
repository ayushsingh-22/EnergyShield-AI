"""Reads chokepoint and port activity trends (Phase 1)."""

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

# IMF PortWatch publishes daily chokepoint transit data via an ArcGIS
# FeatureServer (free, no key). This queries the "Daily Chokepoints"
# layer for the most recent records; the exact layer URL is configurable
# because IMF has revised it over time. Returns GeoJSON-ish JSON with a
# "features" array of {attributes: {...}}.
_PORTWATCH_URL = os.getenv(
    "PORTWATCH_API_URL",
    "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/PortWatch_chokepoints_database/FeatureServer/0/query",
)
_LIVE_FEEDS_ENABLED = os.getenv("ENABLE_LIVE_FEEDS", "false").lower() in ("1", "true", "yes")
# Chokepoints this app cares about; PortWatch names them in a `portname`/
# `chokepoint` attribute we match case-insensitively.
_RELEVANT_CHOKEPOINTS = ("hormuz", "suez", "bab", "mandeb", "malacca", "panama")


class PortwatchCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="portwatch")
        self.reliability = get_source_reliability(self.source_name)

    def _seeded(self) -> List[dict]:
        return [
            {
                "title": "Portwatch: Chokepoint Congestion",
                "summary": "Increased wait times observed at the Suez Canal.",
                "url": "https://example.com/portwatch/suez",
                "language": "en",
                "location_name": "Suez Canal",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

    def _fetch_live(self) -> List[dict] | None:
        payload = fetch_json(
            _PORTWATCH_URL,
            params={
                "where": "1=1",
                "outFields": "portname,vessel_count_total,vessel_count_tanker,share_country_maritime_import",
                "resultRecordCount": "50",
                "f": "json",
            },
            source_name=self.source_name,
            timeout=15.0,
        )
        if not payload or "features" not in payload:
            return None

        items: List[dict] = []
        for feature in payload.get("features", []):
            attrs = feature.get("attributes") or {}
            name = str(attrs.get("portname") or "")
            if not name or not any(keyword in name.lower() for keyword in _RELEVANT_CHOKEPOINTS):
                continue
            total = attrs.get("vessel_count_total")
            tanker = attrs.get("vessel_count_tanker")
            detail = []
            if total is not None:
                detail.append(f"{int(total)} vessels/day")
            if tanker is not None:
                detail.append(f"{int(tanker)} tankers/day")
            summary = f"IMF PortWatch baseline transit for {name}" + (f": {', '.join(detail)}." if detail else ".")
            items.append(
                {
                    "title": f"PortWatch: {name} transit activity",
                    "summary": summary,
                    "url": "https://portwatch.imf.org/",
                    "language": "en",
                    "location_name": name,
                    "published_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        return items or None

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
