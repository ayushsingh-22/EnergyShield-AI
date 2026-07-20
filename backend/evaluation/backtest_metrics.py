"""Shared metric utilities for precision, recall, false alarm rate, missed event rate, and lead time."""

from __future__ import annotations

from datetime import datetime
from typing import Callable, TypeVar

T = TypeVar("T")


def lead_time_seconds(published_at: datetime | None, detected_at: datetime) -> float | None:
    """Signal detection lead time: `detected_at - published_at` (Phase 11
    Evaluation Metrics table). `None` when no publish timestamp is known -
    an unknown lead time, not a zero one."""
    if published_at is None:
        return None
    return (detected_at - published_at).total_seconds()


def precision(true_positives: int, false_positives: int) -> float:
    denominator = true_positives + false_positives
    return round(true_positives / denominator, 4) if denominator else 0.0


def recall(true_positives: int, false_negatives: int) -> float:
    denominator = true_positives + false_negatives
    return round(true_positives / denominator, 4) if denominator else 0.0


def f1_score(precision_value: float, recall_value: float) -> float:
    denominator = precision_value + recall_value
    return round(2 * precision_value * recall_value / denominator, 4) if denominator else 0.0


def false_alarm_rate(false_positives: int, total_predicted_positive: int) -> float:
    return round(false_positives / total_predicted_positive, 4) if total_predicted_positive else 0.0


def missed_event_rate(false_negatives: int, total_actual_positive: int) -> float:
    return round(false_negatives / total_actual_positive, 4) if total_actual_positive else 0.0


def percent_matching(items: list[T], predicate: Callable[[T], bool]) -> float:
    """Percentage of `items` for which `predicate(item)` is true - the
    shared shape behind "risk score explainability" (% with top drivers),
    "scenario fidelity" (% with explicit assumptions), "auditability" (%
    with an audit entry), and similar coverage metrics."""
    if not items:
        return 0.0
    matching = sum(1 for item in items if predicate(item))
    return round(100.0 * matching / len(items), 1)
