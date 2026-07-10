from ingestion.commodity_price_collector import CommodityPriceCollector, SPIKE_THRESHOLD_PERCENT


def test_compute_change_percent_matches_manual_calculation():
    collector = CommodityPriceCollector()
    prices = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 110.0]

    assert collector._compute_change_percent(prices, 1) == round((110.0 - 106.0) / 106.0 * 100, 2)
    assert collector._compute_change_percent(prices, 7) == round((110.0 - 100.0) / 100.0 * 100, 2)


def test_compute_change_percent_returns_none_when_insufficient_history():
    collector = CommodityPriceCollector()
    assert collector._compute_change_percent([100.0, 101.0], 7) is None


def test_fetch_flags_anomaly_when_seeded_series_exceeds_threshold():
    collector = CommodityPriceCollector()
    records = collector.fetch()

    assert len(records) == 1
    record = records[0]
    # The seeded 8-day Brent series rallies well past SPIKE_THRESHOLD_PERCENT
    # over its most recent 7 days, so this must be reported as an anomaly.
    assert record.title == "Brent Crude Price Anomaly"
    assert f"{SPIKE_THRESHOLD_PERCENT:.1f}%" in record.raw_text


def test_fetch_reports_routine_update_when_below_threshold(monkeypatch):
    import ingestion.commodity_price_collector as module

    monkeypatch.setattr(module, "_SEEDED_BRENT_SERIES", [82.0, 82.1, 82.2, 82.1, 82.3, 82.2, 82.4, 82.5])
    collector = module.CommodityPriceCollector()

    records = collector.fetch()

    assert records[0].title == "Brent Crude Daily Price Update"
