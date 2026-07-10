"""Downloads or imports sanctions list snapshots (Phase 1, section 1.4)."""

from __future__ import annotations

import logging
from typing import Any, List
from datetime import datetime, timezone

from ingestion.base_collector import BaseCollector
from ingestion.source_registry import get_source_reliability
from models.data_source_schema import RawSourceRecord

logger = logging.getLogger(__name__)

# Seeded sanctions list snapshot - stands in for a live OFAC/EU/UN pull per
# the Phase 1 fallback contract. Each entry is one sanctioned entity as it
# would appear in a real list snapshot (plan section 1.4, step 1).
_SEEDED_SANCTIONS_SNAPSHOT = [
    {
        "entity_id": "SANC_DELTA_SHIPPING",
        "name": "Delta Shipping Ltd",
        "country": "Global",
        "list_type": "OFAC_SDN",
        "effective_date": "2026-07-01",
    },
    {
        "entity_id": "SANC_NORTHLINE_TANKERS",
        "name": "Northline Tankers Co",
        "country": "Global",
        "list_type": "OFAC_SDN",
        "effective_date": "2026-07-05",
    },
    {
        "entity_id": "SANC_PETROCARRY",
        "name": "Petrocarry Logistics",
        "country": "Global",
        "list_type": "EU_SANCTIONS",
        "effective_date": "2026-07-08",
    },
]


class SanctionsCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="sanctions")
        self.reliability = get_source_reliability(self.source_name)
        # Entities already surfaced by a previous fetch() on *this instance*
        # (plan section 1.4, step 2: "detect new records compared with
        # previous snapshot"). Kept per-instance rather than at module scope
        # so two independent consumers (e.g. the data-freshness bootstrap
        # and the events pipeline, each holding their own collector
        # instance) both see the full snapshot on their own first poll
        # instead of racing each other for who "claims" the delta.
        self._previous_snapshot_entity_ids: set[str] = set()

    def fetch(self) -> List[RawSourceRecord]:
        try:
            new_entities = [
                entity
                for entity in _SEEDED_SANCTIONS_SNAPSHOT
                if entity["entity_id"] not in self._previous_snapshot_entity_ids
            ]
            self._previous_snapshot_entity_ids.update(
                entity["entity_id"] for entity in _SEEDED_SANCTIONS_SNAPSHOT
            )

            if not new_entities:
                logger.info("No new sanctions entries since last snapshot for %s", self.source_name)
                return []

            # step 3: emit SANCTION_UPDATE candidate signals for each delta
            seeded_data = [
                {
                    "title": f"Sanctions update: {entity['name']}",
                    "summary": (
                        f"{entity['name']} ({entity['country']}) added to the {entity['list_type']} list, "
                        f"effective {entity['effective_date']}."
                    ),
                    "url": f"https://example.com/sanctions/{entity['entity_id'].lower()}",
                    "language": "en",
                    "location_name": entity["country"],
                    "published_at": datetime.now(timezone.utc).isoformat(),
                }
                for entity in new_entities
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
