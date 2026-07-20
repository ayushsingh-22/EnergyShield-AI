"""Pulls or loads daily crude price time series and emits price anomaly records (Phase 1, section 1.5)."""

from __future__ import annotations

import logging
import os
from typing import Any, List, Optional
from datetime import datetime, timezone

from ingestion.base_collector import BaseCollector
from ingestion.http_client import fetch_json
from ingestion.source_registry import get_source_reliability
from models.data_source_schema import RawSourceRecord

logger = logging.getLogger(__name__)

# Configured anomaly threshold (plan section 1.5, "detect price spikes over
# configured threshold"): a 1/3/7-day move at or beyond this magnitude is
# reported as an anomaly rather than a routine daily update.
SPIKE_THRESHOLD_PERCENT = 3.0

# Seeded daily Brent close prices (USD/bbl), oldest first - the fallback when
# no live price feed is configured/reachable. Includes a real multi-day rally
# so the threshold/spike logic has something to detect in the demo path.
_SEEDED_BRENT_SERIES = [82.10, 82.40, 81.90, 83.20, 84.00, 85.10, 88.90, 89.30]

# Live price feeds (opt-in via ENABLE_LIVE_FEEDS). EIA v2 is primary (Brent
# daily spot, series RBRTE); Alpha Vantage BRENT is the secondary fallback.
_LIVE_FEEDS_ENABLED = os.getenv("ENABLE_LIVE_FEEDS", "false").lower() in ("1", "true", "yes")
_EIA_API_KEY = os.getenv("EIA_API_KEY", "")
_EIA_BRENT_URL = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
_ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
_ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"


def _format_percent(value: Optional[float]) -> str:
    return f"{value:+.2f}%" if value is not None else "n/a"


class CommodityPriceCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="commodity_prices")
        self.reliability = get_source_reliability(self.source_name)

    def _compute_change_percent(self, prices: List[float], days_back: int) -> Optional[float]:
        """1/3/7-day % change vs. the most recent price (plan section 1.5, step 1)."""
        if len(prices) <= days_back:
            return None
        latest = prices[-1]
        previous = prices[-1 - days_back]
        if previous == 0:
            return None
        return round((latest - previous) / previous * 100, 2)

    def _fetch_eia_series(self) -> Optional[List[float]]:
        """Daily Brent spot series from EIA v2 (oldest-first), or None."""
        if not _EIA_API_KEY:
            return None
        payload = fetch_json(
            _EIA_BRENT_URL,
            params={
                "api_key": _EIA_API_KEY,
                "frequency": "daily",
                "data[0]": "value",
                "facets[series][]": "RBRTE",  # Europe Brent Spot Price FOB (USD/bbl)
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "length": "8",
            },
            source_name=self.source_name,
        )
        try:
            rows = payload["response"]["data"]  # newest-first
            prices = [float(row["value"]) for row in rows if row.get("value") is not None]
            return list(reversed(prices)) or None  # oldest-first for change math
        except (TypeError, KeyError, ValueError):
            return None

    def _fetch_alpha_vantage_series(self) -> Optional[List[float]]:
        """Daily Brent series from Alpha Vantage (oldest-first), or None."""
        if not _ALPHA_VANTAGE_API_KEY:
            return None
        payload = fetch_json(
            _ALPHA_VANTAGE_URL,
            params={"function": "BRENT", "interval": "daily", "apikey": _ALPHA_VANTAGE_API_KEY},
            source_name=self.source_name,
        )
        try:
            data = payload["data"]  # newest-first, {date, value}
            prices = [float(row["value"]) for row in data[:8] if row.get("value") not in (None, ".")]
            return list(reversed(prices)) or None
        except (TypeError, KeyError, ValueError):
            return None

    def _resolve_series(self) -> tuple[List[float], bool]:
        """Returns (price_series, is_live). Tries EIA, then Alpha Vantage,
        then the seeded series."""
        if _LIVE_FEEDS_ENABLED:
            live = self._fetch_eia_series() or self._fetch_alpha_vantage_series()
            if live and len(live) >= 2:
                return live, True
        return _SEEDED_BRENT_SERIES, False

    def fetch(self) -> List[RawSourceRecord]:
        try:
            prices, _is_live = self._resolve_series()
            latest_price = prices[-1]
            changes = {
                "1_day": self._compute_change_percent(prices, 1),
                "3_day": self._compute_change_percent(prices, 3),
                "7_day": self._compute_change_percent(prices, 7),
            }
            max_abs_change = max((abs(value) for value in changes.values() if value is not None), default=0.0)
            is_spike = max_abs_change >= SPIKE_THRESHOLD_PERCENT  # step 2: threshold detection

            change_summary = (
                f"1d {_format_percent(changes['1_day'])}, "
                f"3d {_format_percent(changes['3_day'])}, "
                f"7d {_format_percent(changes['7_day'])}"
            )
            if is_spike:  # step 3: emit as a price anomaly record
                title = "Brent Crude Price Anomaly"
                summary = (
                    f"Brent crude at ${latest_price:.2f}/bbl moved {max_abs_change:.2f}% "
                    f"({change_summary}), exceeding the {SPIKE_THRESHOLD_PERCENT:.1f}% anomaly threshold."
                )
            else:
                title = "Brent Crude Daily Price Update"
                summary = f"Brent crude at ${latest_price:.2f}/bbl ({change_summary}); no anomaly threshold breached."

            seeded_data = [
                {
                    "title": title,
                    "summary": summary,
                    "url": "https://example.com/prices/brent",
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
