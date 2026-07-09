"""Converts all collector outputs into common NormalizedSignal records (Phase 1, section 1.6)."""

from __future__ import annotations

import hashlib
import logging
import uuid
from typing import List, Dict
from datetime import datetime

from models.data_source_schema import RawSourceRecord, NormalizedSignal
from models.core_schema import SourceReliability

logger = logging.getLogger(__name__)

class DataNormalizer:
    def __init__(self):
        # In-memory store to detect duplicates (title hash, url hash, text hash)
        self.seen_hashes: Dict[str, datetime] = {}

    def _compute_hash(self, text: str) -> str:
        if not text:
            return ""
        return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

    def is_duplicate(self, record: RawSourceRecord) -> bool:
        """
        Duplicate detection using normalized title, URL hash, text similarity (via hash),
        and publication timestamp. Only keep newest duplicate.
        """
        hashes_to_check = []
        if record.url:
            hashes_to_check.append(f"url_{self._compute_hash(record.url)}")
        if record.title:
            hashes_to_check.append(f"title_{self._compute_hash(record.title)}")
        if record.raw_text:
            hashes_to_check.append(f"text_{self._compute_hash(record.raw_text)}")

        is_dup = False
        record_time = record.published_at or record.detected_at

        for h in hashes_to_check:
            if h in self.seen_hashes:
                # If we have seen it, check if the incoming record is newer
                existing_time = self.seen_hashes[h]
                if record_time > existing_time:
                    # Update with newest time, but it's still functionally overriding existing
                    # In a real DB we'd update the DB row. Here we just return False so it gets processed,
                    # or True if it's older.
                    # As per instruction: "Only keep newest duplicate."
                    # For a stream processor, if we see an older duplicate we drop it.
                    self.seen_hashes[h] = record_time
                    return False # Keep the newer one (we'll process it)
                else:
                    is_dup = True
            else:
                self.seen_hashes[h] = record_time

        return is_dup

    def normalize(self, raw_records: List[RawSourceRecord]) -> List[NormalizedSignal]:
        normalized_signals = []
        for raw in raw_records:
            if self.is_duplicate(raw):
                logger.info(f"Duplicate detected and dropped: {raw.title or raw.url}")
                continue
            
            signal_id = str(uuid.uuid4())
            # Convert RawSourceRecord to NormalizedSignal
            signal = NormalizedSignal(
                signal_id=signal_id,
                source=raw.source_name,
                source_name=raw.source_name,
                source_reliability=raw.reliability_tier,
                reliability=raw.reliability_tier,
                commodity_type=None,
                published_at=raw.published_at,
                detected_at=raw.detected_at,
                title=raw.title,
                raw_text=raw.raw_text,
                url=raw.url,
                evidence_url=raw.url,
                geo_hint=None,
                corridor_hint=None,
                country_hint=raw.location_name, # Map location_name to country_hint as best effort
                is_simulated=True if raw.reliability_tier == SourceReliability.SIMULATED else False,
                event_candidate=True,
                confidence=1.0 if raw.reliability_tier in [SourceReliability.OFFICIAL, SourceReliability.HIGH] else 0.5,
                raw_record_id=signal_id,
                metadata={
                    "language": raw.language,
                    "original_location": raw.location_name
                }
            )
            normalized_signals.append(signal)

        return normalized_signals
