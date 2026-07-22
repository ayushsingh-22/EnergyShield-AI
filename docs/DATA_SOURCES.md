# Live Data Feeds

EnergyShield's Phase 1 collectors (`backend/ingestion/`) can read **real
external data** or fall back to **seeded sample data**. This is controlled by
one switch plus per-source config in `.env` (copy from `.env.example`).

## Enabling live feeds

```env
ENABLE_LIVE_FEEDS=true
```

When `false` (the default), every collector uses its built-in seeded sample
so the app runs fully offline and deterministically. When `true`, each
collector attempts its real source and **falls back to seeded data** on any
failure (network error, timeout, rate-limit, missing key) — the app never
crashes or blocks on a bad feed.

## Sources

| Collector | Source | Key needed? | Status | Env vars |
|---|---|---|---|---|
| `commodity_price_collector` | **EIA v2** (Brent daily spot `RBRTE`), **Alpha Vantage** (BRENT, secondary) | Yes (free) | ✅ Verified live | `EIA_API_KEY`, `ALPHA_VANTAGE_API_KEY` |
| `lng_price_collector` | **EIA v2** (Henry Hub daily spot `RNGWHHD`, used as an LNG feedstock proxy) | Yes (free) | ✅ Verified live | `EIA_API_KEY` |
| `coal_price_collector` | **World Bank Pink Sheet** (Newcastle, Australia thermal coal benchmark, monthly `.xlsx`) | No | ✅ Verified live | — |
| `sanctions_collector` | **OFAC SDN** CSV (`treasury.gov`) | No | ✅ Verified live | `OFAC_SDN_URL` |
| `portwatch_collector` | **IMF PortWatch** ArcGIS FeatureServer | No | ✅ Verified live | `PORTWATCH_API_URL` |
| `gdelt_collector` | **GDELT DOC 2.1 API** | No | ✅ Live (rate-limited: 1 req / 5 s) | `GDELT_API_URL`, `GDELT_QUERY` |
| `ais_collector` | **AISHub** webservice (Strait of Hormuz box) | Username | ⚠️ Needs `AISHUB_USERNAME` (data-sharing member); seeded until set | `AISHUB_URL`, `AISHUB_USERNAME` |
| `maritime_alert_collector` | (still seeded) | — | Seeded | — |
| `import_baseline_collector` | (still seeded) | — | Seeded | — |

### Notes per source

- **EIA** — get a free key at <https://www.eia.gov/opendata/register.php>. Primary crude-price feed; Alpha Vantage (<https://www.alphavantage.co/support/#api-key>) is tried only if EIA fails. The Henry Hub route (`natural-gas/pri/fut`, series `RNGWHHD`) additionally requires a `start` date param — it silently returns stale rows if `sort`+`length` are used alone.
- **World Bank Pink Sheet** — a public monthly `.xlsx` (`CMO-Historical-Data-Monthly.xlsx`) with no auth needed. Its download URL contains a release-specific hash that changes every month, so `coal_price_collector` resolves the current link from the commodity-markets landing page (<https://www.worldbank.org/en/research/commodity-markets>) on every fetch rather than hardcoding it. The same workbook also has DAP/Urea/Phosphate Rock fertilizer series, not yet wired into a collector.
- **OFAC SDN** — the full Specially Designated Nationals list (CSV, ~5 MB). The collector filters to vessels + energy/maritime-relevant names and caps at 15 new entries per poll.
- **IMF PortWatch** — free ArcGIS layer; the collector reads the chokepoint transit baseline (Hormuz, Suez, Bab el-Mandeb, Malacca, Panama).
- **GDELT** — free, no key, but **hard-limited to one request every 5 seconds** per IP; the scheduler's default 15-minute refresh is well within that. Transient SSL/timeout failures fall back to seeded data.
- **AISHub** — requires joining the AISHub data-sharing program to get a **username** (there is no API key). Rate-limited to **1 request/minute**. Until `AISHUB_USERNAME` is set, this collector uses seeded data.

## Security

`.env` is gitignored (`.gitignore` covers `.env`, `.env.local`,
`backend/.env`, `frontend/.env`). Never commit real keys. If a key is ever
shared over an insecure channel, rotate it at the provider.
