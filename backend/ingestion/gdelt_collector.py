"""Collects latest geopolitical and energy risk news from GDELT/RSS style sources (Phase 1, section 1.2)."""

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

# GDELT DOC 2.1 API is free and needs no key. The query targets energy
# supply-chain risk news; `mode=ArtList&format=json` returns a JSON article
# list. See https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
_GDELT_BASE_URL = os.getenv("GDELT_API_URL", "https://api.gdeltproject.org/api/v2/doc/doc")
_GDELT_QUERY = os.getenv(
    "GDELT_QUERY",
    '(oil OR crude OR tanker OR "strait of hormuz" OR "red sea" OR sanctions OR OPEC) (disruption OR blockade OR attack OR sanctions)',
)
# Live GDELT is opt-in: only queried when ENABLE_LIVE_FEEDS is truthy, so the
# default demo run stays fully offline/deterministic on seeded data.
_LIVE_FEEDS_ENABLED = os.getenv("ENABLE_LIVE_FEEDS", "false").lower() in ("1", "true", "yes")


class GdeltCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="gdelt")
        self.reliability = get_source_reliability(self.source_name)

    def _seeded(self) -> List[dict]:
        return [
            {
                "title": "Hormuz Strait Tensions Rise After Tanker Incident",
                "summary": "Tensions in the Strait of Hormuz have escalated following a maritime incident involving an oil tanker.",
                "url": "https://example.com/news/hormuz-tensions",
                "language": "en",
                "location_name": "Strait of Hormuz",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

    def _fetch_live(self) -> List[dict] | None:
        """Queries the live GDELT DOC API; returns None to trigger seeded
        fallback on any failure."""
        payload = fetch_json(
            _GDELT_BASE_URL,
            params={
                "query": _GDELT_QUERY,
                "mode": "ArtList",
                "format": "json",
                "maxrecords": "25",
                "sort": "DateDesc",
            },
            source_name=self.source_name,
        )
        if not payload or "articles" not in payload:
            return None

        items: List[dict] = []
        for article in payload.get("articles", []):
            seendate = article.get("seendate")  # e.g. "20260721T083000Z"
            published_at = None
            if seendate:
                try:
                    published_at = datetime.strptime(seendate, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).isoformat()
                except ValueError:
                    published_at = None
            items.append(
                {
                    "title": article.get("title"),
                    "summary": article.get("title", ""),  # DOC ArtList has no body; title carries the signal
                    "url": article.get("url"),
                    "language": article.get("language", "en"),
                    "location_name": article.get("sourcecountry"),
                    "published_at": published_at or datetime.now(timezone.utc).isoformat(),
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
