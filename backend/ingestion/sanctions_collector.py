"""Downloads or imports sanctions list snapshots (Phase 1, section 1.4)."""

from __future__ import annotations

import csv
import io
import logging
import os
from typing import Any, List
from datetime import datetime, timezone

from ingestion.base_collector import BaseCollector
from ingestion.http_client import fetch_text
from ingestion.source_registry import get_source_reliability
from models.data_source_schema import RawSourceRecord

logger = logging.getLogger(__name__)

# OFAC's public Specially Designated Nationals (SDN) list - free, no key,
# served as CSV. Columns (no header): ent_num, name, type, program, ...
# We surface only entries relevant to energy/maritime shipping (vessels,
# shipping/petroleum companies), since the full list (~thousands of rows) is
# mostly out of scope for energy supply-chain risk.
_OFAC_SDN_URL = os.getenv("OFAC_SDN_URL", "https://www.treasury.gov/ofac/downloads/sdn.csv")
_LIVE_FEEDS_ENABLED = os.getenv("ENABLE_LIVE_FEEDS", "false").lower() in ("1", "true", "yes")
# Keywords that mark an SDN entry as energy/maritime-relevant for this app.
_RELEVANT_KEYWORDS = ("SHIP", "TANKER", "VESSEL", "PETROL", "OIL", "CRUDE", "LNG", "MARITIME", "PORT")
# Cap how many relevant new entries we emit per poll so one large list update
# doesn't flood the event pipeline.
_MAX_ENTRIES_PER_POLL = 15

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

    def _fetch_live_snapshot(self) -> List[dict] | None:
        """Pulls the live OFAC SDN CSV and returns energy/maritime-relevant
        entries in the same shape as `_SEEDED_SANCTIONS_SNAPSHOT`; returns
        None to trigger seeded fallback."""
        text = fetch_text(_OFAC_SDN_URL, source_name=self.source_name, timeout=30.0)
        if not text:
            return None

        snapshot: List[dict] = []
        for row in csv.reader(io.StringIO(text)):
            if len(row) < 4:
                continue
            ent_num, name, sdn_type, program = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()
            if not name or name == "-0-":
                continue
            # Vessels are directly relevant; otherwise match energy/maritime
            # keywords in the entity name so we surface shipping/petroleum
            # companies without pulling in the entire (mostly irrelevant) list.
            is_vessel = sdn_type.upper() == "VESSEL"
            if not is_vessel and not any(keyword in name.upper() for keyword in _RELEVANT_KEYWORDS):
                continue
            snapshot.append(
                {
                    "entity_id": f"SANC_OFAC_{ent_num}",
                    "name": name.title() if name.isupper() else name,
                    "country": program or "Global",
                    "list_type": "OFAC_SDN",
                    "effective_date": datetime.now(timezone.utc).date().isoformat(),
                }
            )
            if len(snapshot) >= _MAX_ENTRIES_PER_POLL:
                break
        return snapshot or None

    def fetch(self) -> List[RawSourceRecord]:
        try:
            snapshot = self._fetch_live_snapshot() if _LIVE_FEEDS_ENABLED else None
            if snapshot is None:
                snapshot = _SEEDED_SANCTIONS_SNAPSHOT

            new_entities = [
                entity
                for entity in snapshot
                if entity["entity_id"] not in self._previous_snapshot_entity_ids
            ]
            self._previous_snapshot_entity_ids.update(entity["entity_id"] for entity in snapshot)

            if not new_entities:
                logger.info("No new sanctions entries since last snapshot for %s", self.source_name)
                return []

            # step 3: emit SANCTION_UPDATE candidate signals for each delta
            data = [
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
