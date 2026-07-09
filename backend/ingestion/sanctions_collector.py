"""Downloads or imports sanctions list snapshots (Phase 1, section 1.4)."""

from __future__ import annotations

import logging
from typing import Any, List
from datetime import datetime, timezone

from ingestion.base_collector import BaseCollector
from ingestion.source_registry import get_source_reliability
from models.data_source_schema import RawSourceRecord

logger = logging.getLogger(__name__)

class SanctionsCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="sanctions")
        self.reliability = get_source_reliability(self.source_name)

    def fetch(self) -> List[RawSourceRecord]:
        try:
            seeded_data = [
                {
                    "title": "OFAC Sanctions Update: Shipping Entities",
                    "summary": "New sanctions placed on shipping companies involved in illicit crude transport.",
                    "url": "https://example.com/sanctions/update",
                    "language": "en",
                    "location_name": "Global",
                    "published_at": datetime.now(timezone.utc).isoformat()
                }
            ]
            return self.normalize(seeded_data)
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
