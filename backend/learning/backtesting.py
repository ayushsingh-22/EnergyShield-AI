"""Replays historical disruption cases through the current model and computes backtest metrics (Phase 13, section 13.4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from evaluation.backtest_metrics import false_alarm_rate, missed_event_rate, precision, recall
from learning.disruption_case_library import DisruptionCaseLibrary
from learning.label_builder import build_labels
from models.core_schema import RiskLevel
from models.learning_schema import HistoricalCase
from models.scenario_schema import ScenarioRequest, ScenarioType
from scenarios.scenario_engine import ScenarioEngine

# Which scenario template a historical case's affected corridor most
# directly corresponds to, so the current model can be replayed against
# it (section 13.4, step 1: "run risk model at each historical
# timestamp" - simplified to "run the current scenario engine against the
# case's real-world corridor", since no live historical event/price feed
# exists in this prototype).
_CORRIDOR_SCENARIO_MAP: dict[str, ScenarioType] = {
    "HORMUZ": ScenarioType.HORMUZ_PARTIAL_CLOSURE,
    "RED_SEA": ScenarioType.RED_SEA_SHIPPING_DISRUPTION,
    "SUEZ": ScenarioType.RED_SEA_SHIPPING_DISRUPTION,
    "BAB_EL_MANDEB": ScenarioType.RED_SEA_SHIPPING_DISRUPTION,
}

# A predicted supply_at_risk_percent at/above this is treated as the
# model flagging the case as materially disruptive - mirrors the same
# order of magnitude `scenarios/scenario_engine.py` uses for
# `recommended_action_required`. Exposed as a parameter (not just this
# default) so `learning/model_trainer.py` can grid-search calibration
# candidates without monkeypatching module state.
DEFAULT_FLAG_THRESHOLD_PERCENT = 15.0


@dataclass
class BacktestCaseResult:
    case_id: str
    scenario_type: ScenarioType | None
    predicted_materially_disruptive: bool
    observed_materially_disruptive: bool
    predicted_supply_at_risk_percent: float | None
    predicted_confidence: float | None


@dataclass
class BacktestReport:
    run_id: str
    case_results: list[BacktestCaseResult] = field(default_factory=list)
    precision: float = 0.0
    recall: float = 0.0
    false_alarm_rate: float = 0.0
    missed_event_rate: float = 0.0


def _resolve_scenario_type(case: HistoricalCase) -> ScenarioType | None:
    for corridor in case.affected_corridors:
        scenario_type = _CORRIDOR_SCENARIO_MAP.get(corridor)
        if scenario_type is not None:
            return scenario_type
    return None


def run_backtest(
    cases: list[HistoricalCase] | None = None,
    *,
    case_library: DisruptionCaseLibrary | None = None,
    scenario_engine: ScenarioEngine | None = None,
    run_id: str | None = None,
    flag_threshold_percent: float = DEFAULT_FLAG_THRESHOLD_PERCENT,
) -> BacktestReport:
    """Section 13.4: replays every historical case through the current
    scenario engine, compares its "materially disruptive" call against the
    case's actual observed outcome, and aggregates the standard detection
    metrics from `evaluation.backtest_metrics` - the same shared utilities
    Phase 11 uses for live evaluation."""
    if cases is None:
        case_library = case_library or DisruptionCaseLibrary()
        if not case_library.get_all():
            case_library.load_seed_data()
        cases = case_library.get_all()

    engine = scenario_engine or ScenarioEngine()
    labels = {label.case_id: label for label in build_labels(cases)}

    case_results: list[BacktestCaseResult] = []
    true_positives = false_positives = false_negatives = 0

    for case in cases:
        scenario_type = _resolve_scenario_type(case)
        label = labels[case.case_id]
        predicted_flag = False
        predicted_percent = None
        predicted_confidence = None

        if scenario_type is not None:
            duration_days = max((case.end_date - case.start_date).days, 1) if case.end_date else 15
            result = engine.run(
                ScenarioRequest(
                    scenario_type=scenario_type,
                    commodity_type=case.commodity_type,
                    duration_days=duration_days,
                    severity=RiskLevel.HIGH,
                    affected_entities=[],
                ),
                scenario_id=f"BACKTEST-{case.case_id}",
                created_at=datetime.now(timezone.utc),
            )
            predicted_percent = result.supply_at_risk_percent
            predicted_confidence = result.confidence
            predicted_flag = result.supply_at_risk_percent >= flag_threshold_percent

        observed_flag = label.materially_disruptive
        if predicted_flag and observed_flag:
            true_positives += 1
        elif predicted_flag and not observed_flag:
            false_positives += 1
        elif not predicted_flag and observed_flag:
            false_negatives += 1

        case_results.append(
            BacktestCaseResult(
                case_id=case.case_id,
                scenario_type=scenario_type,
                predicted_materially_disruptive=predicted_flag,
                observed_materially_disruptive=observed_flag,
                predicted_supply_at_risk_percent=predicted_percent,
                predicted_confidence=predicted_confidence,
            )
        )

    precision_value = precision(true_positives, false_positives)
    recall_value = recall(true_positives, false_negatives)
    return BacktestReport(
        run_id=run_id or f"BT-{datetime.now(timezone.utc):%Y%m%d%H%M%S}",
        case_results=case_results,
        precision=precision_value,
        recall=recall_value,
        false_alarm_rate=false_alarm_rate(false_positives, true_positives + false_positives),
        missed_event_rate=missed_event_rate(false_negatives, true_positives + false_negatives),
    )
