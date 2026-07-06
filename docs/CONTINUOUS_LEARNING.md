# EnergyShield AI - Continuous Learning

Summary of Phase 13 (`ENERGYSHIELD_IMPLEMENTATION_PLAN.md`). Continuous
learning calibrates event severity weights, source reliability weighting,
risk thresholds, and recommendation quality using historical disruptions,
backtests, and human feedback (Planning Principle #7), without ever
rewriting the audit record of what the platform actually recommended at
the time.

## Learning Pipeline

```text
Disruption Case Library
  -> Feature Store
  -> Label Builder
  -> Backtesting
  -> Model Trainer
  -> Model Registry
  -> Feedback Service (continuously feeds back into Feature Store / Label Builder)
```

| Stage | Module | Role |
| --- | --- | --- |
| Disruption case library | `backend/learning/disruption_case_library.py` | Stores curated historical disruption cases (see `data/seeds/demo_disruption_cases.json` for seed examples) with trigger events, affected corridors, and observed outcomes |
| Feature store | `backend/learning/feature_store.py` | Stores the feature vector (event severity, source reliability, price movement, AIS anomaly, graph exposure) that was available at each historical timestamp, linked to the model version that consumed it |
| Label builder | `backend/learning/label_builder.py` | Converts observed outcomes (delay days, price movement, rerouting) into labels: materiality, delay band, price-impact band, reroute-occurred |
| Backtesting | `backend/learning/backtesting.py` | Replays historical cases through the current (and candidate) risk model, scoring precision, recall, false-alarm rate, missed-event rate, and detection lead time |
| Model trainer | `backend/learning/model_trainer.py` | Calibrates risk score weights and scenario trigger thresholds (logistic regression / gradient boosting / Bayesian calibration); compares against the rule-based baseline before accepting a new version |
| Model registry | `backend/learning/model_registry.py` | Tracks every model/rule version with its training data range, metrics, owner, and status (`candidate`, `active`, `archived`) |
| Feedback service | `backend/learning/feedback_service.py` | Captures analyst accept/reject/modify feedback on recommendations from the dashboard and routes it back into future label building |

## Historical Case Schema

```json
{
  "case_id": "CASE-REDSEA-2024-001",
  "case_name": "Red Sea shipping disruption sample case",
  "commodity_type": "CRUDE_OIL",
  "start_date": "2024-01-01",
  "end_date": "2024-02-15",
  "trigger_events": ["MARITIME_ATTACK", "AIS_REROUTING"],
  "affected_corridors": ["RED_SEA", "SUEZ"],
  "observed_outcomes": {
    "average_delay_days": 12,
    "freight_cost_increase_percent": 20,
    "route_shift_detected": true,
    "price_movement_percent": 6
  },
  "source_notes": "Public data or simulated historical case notes",
  "is_simulated": true
}
```

`data/seeds/demo_disruption_cases.json` seeds three illustrative cases
built around real disruptions (2023-24 Red Sea/Houthi attacks, 2019 Hormuz
tanker incidents, 2022 post-invasion Russian crude reroute) with
`is_simulated: true` and source notes stating the outcome figures are
illustrative, not audited historical statistics - consistent with Planning
Principle #9.

## Evaluation Metrics Produced

| Metric | Produced By | What It Measures |
| --- | --- | --- |
| Precision / recall | `backtesting.py` | Did the model flag real disruptions without excessive false alarms? |
| False alarm rate | `backtesting.py` | Share of high-risk predictions with no corresponding historical disruption |
| Missed event rate | `backtesting.py` | Share of historical disruptions the model would not have flagged |
| Detection lead time | `backtesting.py` | Time between when the model would have crossed a risk threshold and when the disruption materially began |
| Calibration error | `model_trainer.py` | Gap between predicted risk probability and observed outcome frequency |
| Recommendation usefulness | `feedback_service.py` | Share of recommendations analysts accepted vs. rejected/modified, with reasons |

These roll up into the `LearningCenter.jsx` dashboard (model versions,
backtest results, feedback history) and into `/api/v1/learning/*` (Phase
13 API contract: `GET /learning/cases`, `POST /learning/backtest`, `POST
/learning/feedback`, `GET /learning/models`, `POST
/learning/models/{model_id}/activate`).

## Governance Rule: No Overwriting Past Scenario Results

**A new model version must never overwrite the stored output of a scenario
or recommendation that already ran under a previous model version.**

This is enforced by the model registry and feature store working together:

1. Every `ScenarioResult` and `Recommendation` persists the `model_version`
   (or rule-set version) that produced it, alongside its feature vector
   snapshot in `feature_store.py`.
2. `model_registry.py` never deletes or mutates an `archived` version's
   metadata - only its `status` field transitions (`candidate` ->
   `active` -> `archived`).
3. Activating a new model version (`POST
   /api/v1/learning/models/{model_id}/activate`) changes which version
   *future* risk scores and scenarios use; it does not retroactively
   recompute or replace past results.
4. Audit replay (Phase 11) must be able to reconstruct exactly what any
   given scenario/recommendation looked like at the time it was generated,
   using only the model version and feature snapshot recorded with it.

This trades away "clean" retroactively-corrected history for auditability:
an analyst reviewing why a SPR drawdown was recommended in the past must
see the model and assumptions that were actually active then, not a
result recomputed with hindsight.

## Deployment Gate

Per the Phase 13 validation checklist, a candidate model is only promoted
to `active` when its backtest metrics improve on the currently active
model on the same historical case set - guarding against the risk-register
concern that "continuous learning overfits small historical data" by
requiring conservative, metric-gated promotion rather than automatic
retraining/redeployment.
