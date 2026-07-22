"""Pulls or loads monthly Newcastle (Australia) thermal coal prices from the
World Bank's "Pink Sheet" commodity price data and emits price anomaly
records, mirroring `commodity_price_collector.py` (Phase 1, section 1.5) for
the Coal commodity (Phase 14 multi-commodity expansion).

The Pink Sheet's historical-data workbook lives at a URL whose path segment
changes with every monthly release, so this collector first resolves the
current URL from the commodity-markets landing page rather than hardcoding
it. The workbook itself is a public, no-auth `.xlsx` download published
monthly by the World Bank - confirmed live during development (see
docs/DATA_SOURCES.md).
"""

from __future__ import annotations

import io
import logging
import os
import re
from typing import Any, List, Optional
from datetime import datetime, timezone

import httpx

from ingestion.base_collector import BaseCollector
from ingestion.source_registry import get_source_reliability
from models.data_source_schema import RawSourceRecord

logger = logging.getLogger(__name__)

SPIKE_THRESHOLD_PERCENT = 3.0

# Seeded monthly Newcastle coal prices (USD/tonne), oldest first - fallback
# when no live feed is configured/reachable.
_SEEDED_NEWCASTLE_COAL_SERIES = [107.7, 109.8, 118.4, 138.6, 130.9, 136.9, 138.5]

_LIVE_FEEDS_ENABLED = os.getenv("ENABLE_LIVE_FEEDS", "false").lower() in ("1", "true", "yes")
_WORLD_BANK_LANDING_PAGE = "https://www.worldbank.org/en/research/commodity-markets"
_XLSX_LINK_PATTERN = re.compile(r'href="([^"]+CMO-Historical-Data-Monthly\.xlsx)"')
_SHEET_NAME = "Monthly Prices"
_COAL_COLUMN_HEADER = "Coal, Australian"
_REQUEST_TIMEOUT_SECONDS = 20.0


class CoalPriceCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="coal_prices")
        self.reliability = get_source_reliability(self.source_name)

    def _compute_change_percent(self, prices: List[float], periods_back: int) -> Optional[float]:
        if len(prices) <= periods_back:
            return None
        latest = prices[-1]
        previous = prices[-1 - periods_back]
        if previous == 0:
            return None
        return round((latest - previous) / previous * 100, 2)

    def _resolve_workbook_url(self) -> Optional[str]:
        """Finds the current month's Pink Sheet workbook URL from the
        commodity-markets landing page (the URL's path segment rotates
        every monthly release)."""
        try:
            response = httpx.get(
                _WORLD_BANK_LANDING_PAGE,
                timeout=_REQUEST_TIMEOUT_SECONDS,
                follow_redirects=True,
                headers={"User-Agent": "EnergyShield-AI/0.1 (ingestion)"},
            )
            response.raise_for_status()
            match = _XLSX_LINK_PATTERN.search(response.text)
            return match.group(1) if match else None
        except Exception as exc:  # noqa: BLE001 - external source, must not crash pipeline
            logger.info("Could not resolve World Bank Pink Sheet URL (%s); falling back to seeded data.", exc)
            return None

    def _fetch_worldbank_series(self) -> Optional[List[float]]:
        """Monthly Newcastle coal price series from the World Bank Pink
        Sheet (oldest-first), or None."""
        workbook_url = self._resolve_workbook_url()
        if not workbook_url:
            return None
        try:
            import openpyxl  # local import: optional dependency only needed on the live path

            response = httpx.get(
                workbook_url,
                timeout=_REQUEST_TIMEOUT_SECONDS,
                follow_redirects=True,
                headers={"User-Agent": "EnergyShield-AI/0.1 (ingestion)"},
            )
            response.raise_for_status()
            workbook = openpyxl.load_workbook(io.BytesIO(response.content), data_only=True, read_only=True)
            sheet = workbook[_SHEET_NAME]

            header_row = None
            coal_column_index = None
            rows = sheet.iter_rows(values_only=True)
            for row in rows:
                if _COAL_COLUMN_HEADER in row:
                    header_row = row
                    coal_column_index = row.index(_COAL_COLUMN_HEADER)
                    break
            if header_row is None or coal_column_index is None:
                return None

            prices = [
                float(row[coal_column_index])
                for row in rows
                if row[coal_column_index] is not None
            ]
            return prices[-8:] or None  # oldest-first, most recent 8 months
        except Exception as exc:  # noqa: BLE001 - external source, must not crash pipeline
            logger.info("World Bank Pink Sheet fetch/parse failed (%s); falling back to seeded data.", exc)
            return None

    def _resolve_series(self) -> tuple[List[float], bool]:
        """Returns (price_series, is_live). Tries the World Bank Pink
        Sheet, then the seeded series."""
        if _LIVE_FEEDS_ENABLED:
            live = self._fetch_worldbank_series()
            if live and len(live) >= 2:
                return live, True
        return _SEEDED_NEWCASTLE_COAL_SERIES, False

    def fetch(self) -> List[RawSourceRecord]:
        try:
            prices, _is_live = self._resolve_series()
            latest_price = prices[-1]
            changes = {
                "1_month": self._compute_change_percent(prices, 1),
                "3_month": self._compute_change_percent(prices, 3),
            }
            max_abs_change = max((abs(value) for value in changes.values() if value is not None), default=0.0)
            is_spike = max_abs_change >= SPIKE_THRESHOLD_PERCENT

            change_summary = (
                f"1mo {changes['1_month']:+.2f}%" if changes["1_month"] is not None else "1mo n/a"
            ) + ", " + (
                f"3mo {changes['3_month']:+.2f}%" if changes["3_month"] is not None else "3mo n/a"
            )
            if is_spike:
                title = "Newcastle Coal Price Anomaly"
                summary = (
                    f"Newcastle (Australia) thermal coal at ${latest_price:.2f}/tonne moved {max_abs_change:.2f}% "
                    f"({change_summary}), exceeding the {SPIKE_THRESHOLD_PERCENT:.1f}% anomaly threshold."
                )
            else:
                title = "Newcastle Coal Monthly Price Update"
                summary = (
                    f"Newcastle (Australia) thermal coal at ${latest_price:.2f}/tonne ({change_summary}); "
                    "no anomaly threshold breached."
                )

            seeded_data = [
                {
                    "title": title,
                    "summary": summary,
                    "url": "https://www.worldbank.org/en/research/commodity-markets",
                    "language": "en",
                    "location_name": "Global",
                    "published_at": datetime.now(timezone.utc).isoformat(),
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
