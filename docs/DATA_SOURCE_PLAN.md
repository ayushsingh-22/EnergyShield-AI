# EnergyShield AI - Data Source Plan

Real-time news and social signals are treated as unreliable until validated
by multiple sources or an official channel (Planning Principle #3). Every
collector must degrade to seeded sample data rather than crash the pipeline
when a live source is unavailable (Phase 1 validation checklist).

## MVP Sources

| Signal Type | Prototype Source | Update Frequency | Reliability Tier | Fallback |
| --- | --- | --- | --- | --- |
| Global news and geopolitical events | GDELT or configured RSS feeds | 15-30 min | Medium | Seeded article sample inline in `gdelt_collector.py` |
| Maritime security alerts | UKMTO, MARAD, MSCIO, IMB | 15-30 min | Official / High | Seeded alert inline in `maritime_alert_collector.py` |
| Sanctions | OFAC, EU, UN lists | Daily | Official | Seeded snapshot inline in `sanctions_collector.py`, diffed per-instance against what it already returned |
| Oil prices | EIA or FRED daily Brent/WTI | Daily | High | Seeded 8-day Brent series inline in `commodity_price_collector.py` |
| Chokepoint / port activity | IMF PortWatch | Weekly | High | Seeded trend sample inline in `portwatch_collector.py` |
| AIS vessel movement | AISStream or sample AIS files | Live / batch demo | Low-Medium | Seeded sample inline in `ais_collector.py` |
| India crude import baseline | PPAC, TradeStat | Monthly / manual | High / Simulated | Seeded sample inline in `import_baseline_collector.py`, marked `is_simulated` |
| Geospatial layers | OSM, Natural Earth | Static / manual | High | Checked-in GeoJSON in `data/seeds/` (this is the one category that genuinely lives under `data/seeds/` today - see note below) |

Note: only the digital-twin geospatial/CSV files (`data/seeds/*.csv`,
`*.geojson` - suppliers, ports, refineries, SPR sites, chokepoints, routes)
are externalized to `data/seeds/`. The seven ingestion collectors above
each embed their fallback sample directly in the collector module rather
than reading from `data/seeds/` - a real live-source integration would
still hit `data/seeds/` as its offline fallback path, but that migration
hasn't happened yet.

## Collector-to-Schema Mapping

Every collector in `backend/ingestion/` returns `RawSourceRecord` objects
(`backend/models/data_source_schema.py`), which `data_normalizer.py`
converts to `NormalizedSignal`. Raw text, source URL, and detected/published
timestamps are preserved through both stages so nothing is lost before it
reaches the event extraction agent (Phase 4).

| Collector | Emits | Consumed by |
| --- | --- | --- |
| `gdelt_collector.py` | News `RawSourceRecord` | `data_normalizer.py` -> event extraction |
| `maritime_alert_collector.py` | Advisory `RawSourceRecord` (Official/High) | `data_normalizer.py` -> event extraction |
| `sanctions_collector.py` | Sanctions delta records | `SANCTION_UPDATE` event candidates |
| `commodity_price_collector.py` | Price anomaly records | `PRICE_SPIKE` event candidates, risk scoring |
| `ais_collector.py` | AIS anomaly records | `AIS_REROUTING` event candidates, risk scoring |
| `portwatch_collector.py` | Chokepoint/port trend records | Corridor risk scoring |
| `import_baseline_collector.py` | India import share baseline | Not yet wired to a consumer - `services/digital_twin_service.py` reads `data/seeds/crude_suppliers.csv` directly instead of through this collector; only invoked today by the `/data/freshness` bootstrap |

## Reliability Tiers

`SourceReliability` (`backend/models/core_schema.py`): `OFFICIAL` > `HIGH` >
`MEDIUM` > `LOW` > `SIMULATED`. Reliability tier feeds directly into event
confidence scoring (Phase 4) and the risk formula's source reliability term
(Phase 5) - it is never inferred ad hoc in downstream code.

## Freshness Monitoring

`backend/ingestion/source_registry.py` is the single source of truth for
source metadata (URL, refresh interval, reliability tier, fallback mode).
`GET /api/v1/data/freshness` surfaces `SourceFreshness` records so the
dashboard and operators can see which sources are stale or failing without
digging through logs.

## Known Gaps for MVP (tracked, not blocking)

- Free AIS coverage is incomplete; treat AIS-derived signals as directional,
  not authoritative, until corroborated by PortWatch or maritime alerts.
- Exact cargo ownership, tanker availability, and refinery contract terms
  are not publicly available; these are simulated and explicitly marked
  `is_simulated: true` wherever they appear (scenario and recommendation
  outputs).
- India import baseline is refreshed manually/monthly; scenario confidence
  should be discounted accordingly when baseline age exceeds one quarter.
