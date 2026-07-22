"""Pulls or loads daily Henry Hub natural gas price time series as an LNG price
proxy and emits price anomaly records, mirroring `commodity_price_collector.py`
(Phase 1, section 1.5) for the LNG commodity (Phase 14 multi-commodity expansion).

Henry Hub is used as the LNG feedstock/benchmark proxy rather than a
delivered-LNG price because EIA publishes it daily with no additional
signup beyond the API key this project already has (`EIA_API_KEY`).
"""

from __future__ import annotations

import logging
import os
from typing import Any, List, Optional
from datetime import datetime, timedelta, timezone

from ingestion.base_collector import BaseCollector
from ingestion.http_client import fetch_json
from ingestion.source_registry import get_source_reliability
from models.data_source_schema import RawSourceRecord

logger = logging.getLogger(__name__)

SPIKE_THRESHOLD_PERCENT = 3.0

# Seeded daily Henry Hub spot prices (USD/MMBtu), oldest first - fallback
# when no live feed is configured/reachable.
_SEEDED_HENRY_HUB_SERIES = [2.55, 2.61, 2.58, 2.70, 2.66, 2.75, 2.90, 2.83]

_LIVE_FEEDS_ENABLED = os.getenv("ENABLE_LIVE_FEEDS", "false").lower() in ("1", "true", "yes")
_EIA_API_KEY = os.getenv("EIA_API_KEY", "")
_EIA_HENRY_HUB_URL = "https://api.eia.gov/v2/natural-gas/pri/fut/data/"


def _format_percent(value: Optional[float]) -> str:
    return f"{value:+.2f}%" if value is not None else "n/a"


class LngPriceCollector(BaseCollector):
    def __init__(self):
        super().__init__(source_name="lng_prices")
        self.reliability = get_source_reliability(self.source_name)

    def _compute_change_percent(self, prices: List[float], days_back: int) -> Optional[float]:
        if len(prices) <= days_back:
            return None
        latest = prices[-1]
        previous = prices[-1 - days_back]
        if previous == 0:
            return None
        return round((latest - previous) / previous * 100, 2)

    def _fetch_eia_series(self) -> Optional[List[float]]:
        """Daily Henry Hub spot series from EIA v2 (oldest-first), or None.

        The route ignores `sort`+`length` alone and returns stale rows unless
        a `start` date is also given, so this always constrains the request
        to the last ~30 days before taking the most recent 8 values.
        """
        if not _EIA_API_KEY:
            return None
        start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        payload = fetch_json(
            _EIA_HENRY_HUB_URL,
            params={
                "api_key": _EIA_API_KEY,
                "frequency": "daily",
                "data[0]": "value",
                "facets[series][]": "RNGWHHD",  # Henry Hub Natural Gas Spot Price (USD/MMBtu)
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "start": start_date,
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

    def _resolve_series(self) -> tuple[List[float], bool]:
        """Returns (price_series, is_live). Tries EIA Henry Hub, then the
        seeded series."""
        if _LIVE_FEEDS_ENABLED:
            live = self._fetch_eia_series()
            if live and len(live) >= 2:
                return live, True
        return _SEEDED_HENRY_HUB_SERIES, False

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
            is_spike = max_abs_change >= SPIKE_THRESHOLD_PERCENT

            change_summary = (
                f"1d {_format_percent(changes['1_day'])}, "
                f"3d {_format_percent(changes['3_day'])}, "
                f"7d {_format_percent(changes['7_day'])}"
            )
            if is_spike:
                title = "Henry Hub Natural Gas Price Anomaly"
                summary = (
                    f"Henry Hub natural gas at ${latest_price:.2f}/MMBtu moved {max_abs_change:.2f}% "
                    f"({change_summary}), exceeding the {SPIKE_THRESHOLD_PERCENT:.1f}% anomaly threshold. "
                    "Used as an LNG feedstock price proxy."
                )
            else:
                title = "Henry Hub Natural Gas Daily Price Update"
                summary = (
                    f"Henry Hub natural gas at ${latest_price:.2f}/MMBtu ({change_summary}); "
                    "no anomaly threshold breached. Used as an LNG feedstock price proxy."
                )

            seeded_data = [
                {
                    "title": title,
                    "summary": summary,
                    "url": "https://www.eia.gov/naturalgas/",
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
