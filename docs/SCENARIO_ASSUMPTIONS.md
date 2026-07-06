# EnergyShield AI - Scenario Assumptions

Every scenario run must expose its assumptions in the output
(`ScenarioResult.assumptions`, see `backend/models/scenario_schema.py`) so a
non-technical reviewer can see exactly what is estimated versus observed
(Planning Principle #5). This document is the human-readable counterpart:
the full parameter set for each template lives in
`backend/scenarios/templates/*.yaml`.

## MVP Scenario Templates

| Scenario | Scenario ID | Main Impact Modelled |
| --- | --- | --- |
| Strait of Hormuz partial closure | `HORMUZ_PARTIAL_CLOSURE` | Middle East supply exposure, transit delays, price pressure |
| Red Sea shipping disruption | `RED_SEA_SHIPPING_DISRUPTION` | Suez route delay, Cape of Good Hope rerouting, freight cost increase |
| OPEC+ emergency supply cut | `OPEC_SUPPLY_CUT` | Supplier availability reduction, spot price pressure |
| Sanctions shock | `SANCTIONS_SHOCK` | Supplier feasibility, payment/logistics risk |
| Indian import port congestion | `PORT_CONGESTION` | Arrival delays, refinery run-rate risk |

Phase 14 adds `LNG_SUPPLY_SHOCK`, `COAL_IMPORT_DISRUPTION`,
`FERTILIZER_FEEDSTOCK_SHOCK`, and `CRITICAL_MINERAL_EXPORT_RESTRICTION`
following the same template structure.

## Standing Assumptions Across All Scenarios

1. **Import share data is estimated.** Baseline supplier shares come from
   PPAC/TradeStat snapshots refreshed monthly at best; treat as directional.
2. **Exact cargo ownership, tanker availability, and refinery-grade
   compatibility are simulated** unless a specific data source is cited.
   These fields always carry `is_simulated: true`.
3. **Duration bands are illustrative, not predictive.** A scenario's
   `duration_days` is a user- or trigger-supplied input, not a forecast of
   how long a real disruption will last.
4. **Freight cost and delay coefficients are calibration targets.** Initial
   values are analyst judgment; Phase 13 continuous learning backtests and
   recalibrates them against historical disruption cases.
5. **Refinery exposure is graph-derived, not contractual.** Exposure comes
   from which routes/ports feed a refinery in the knowledge graph, not from
   actual offtake contracts (which are not public).

## Confidence Discounting Rules

`ScenarioResult.confidence` should be reduced when:

- The scenario relies on `manual_overrides` instead of graph/exposure-derived
  defaults.
- Any `affected_refineries` entry has `exposure_level` derived from a route
  with fewer than one corroborating risk event.
- The India import baseline used is older than one quarter.

## Template File Structure

Each `backend/scenarios/templates/<scenario>.yaml` file defines, at minimum:

```yaml
scenario_type: HORMUZ_PARTIAL_CLOSURE
commodity_type: CRUDE_OIL
default_duration_days: 15
supply_reduction_percent_range: [10, 35]
freight_cost_increase_percent_range: [8, 25]
affected_chokepoints: [HORMUZ]
assumptions:
  - "Import share data is estimated"
  - "Exact cargo ownership is simulated"
```

`scenario_engine.py` loads the template matching the request's
`scenario_type`, applies any `manual_overrides`, and always copies the
template's `assumptions` (plus any additional ones triggered by low-quality
inputs) into the response.
