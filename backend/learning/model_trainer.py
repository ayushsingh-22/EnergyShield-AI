"""Trains or calibrates risk model weights and scenario trigger thresholds (Phase 13, section 13.5)."""

from __future__ import annotations

from dataclasses import dataclass

from evaluation.backtest_metrics import f1_score
from learning.backtesting import DEFAULT_FLAG_THRESHOLD_PERCENT, run_backtest
from models.learning_schema import HistoricalCase

# Candidate flag thresholds to grid-search over. A full learned model
# (logistic regression / gradient boosting / Bayesian calibration, per
# section 13.5's suggested approaches) needs a labelled dataset larger
# than the handful of seeded demo cases this prototype ships with; until
# then, calibration is an honest, auditable grid search over the same
# rule-based threshold the scenario engine already uses - see
# `CalibrationResult.notes`.
_CANDIDATE_THRESHOLDS = [10.0, 15.0, 20.0, 25.0, 30.0]


@dataclass
class CalibrationResult:
    baseline_threshold: float
    candidate_threshold: float
    baseline_f1: float
    candidate_f1: float
    improved: bool
    notes: str


def calibrate_flag_threshold(
    cases: list[HistoricalCase], baseline_threshold: float = DEFAULT_FLAG_THRESHOLD_PERCENT
) -> CalibrationResult:
    """Section 13.5, steps 2-4: "calibrate scenario trigger thresholds",
    "compare learned model against rule-based baseline", "store new
    version only if metrics improve". Returns the best-scoring threshold
    found and whether it actually beats the current baseline - the caller
    (`model_registry.py`) only promotes a new version when `improved` is
    True, per the Phase 13 deployment gate."""

    def _f1_for_threshold(threshold: float) -> float:
        report = run_backtest(cases, flag_threshold_percent=threshold)
        return f1_score(report.precision, report.recall)

    baseline_f1 = _f1_for_threshold(baseline_threshold)
    best_threshold, best_f1 = baseline_threshold, baseline_f1
    for candidate in _CANDIDATE_THRESHOLDS:
        candidate_f1 = _f1_for_threshold(candidate)
        if candidate_f1 > best_f1:
            best_threshold, best_f1 = candidate, candidate_f1

    return CalibrationResult(
        baseline_threshold=baseline_threshold,
        candidate_threshold=best_threshold,
        baseline_f1=baseline_f1,
        candidate_f1=best_f1,
        improved=best_f1 > baseline_f1,
        notes=(
            "Grid-search threshold calibration over the seeded demo case set; "
            "not a trained statistical model. Treat as illustrative until a "
            "larger labelled historical dataset is available."
        ),
    )
