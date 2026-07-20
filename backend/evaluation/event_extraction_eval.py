"""Event extraction precision checks on seeded/labelled data."""

from __future__ import annotations

from dataclasses import dataclass

from evaluation.backtest_metrics import percent_matching
from models.event_schema import RiskEvent


@dataclass
class LabelledSample:
    """One hand-labelled ground-truth signal for accuracy scoring."""

    expected_event_type: str
    expected_affected_entities: set[str]
    extracted_event: RiskEvent | None


def event_extraction_accuracy(samples: list[LabelledSample]) -> dict[str, float | int]:
    """Fraction of labelled samples where the extracted event's type
    matches and at least one affected entity overlaps the label (Phase 11
    Evaluation Metrics table: "Event extraction accuracy")."""
    correct = 0
    missed = 0
    for sample in samples:
        event = sample.extracted_event
        if event is None:
            missed += 1
            continue
        type_matches = event.event_type == sample.expected_event_type
        entity_overlap = bool(sample.expected_affected_entities.intersection(event.affected_entities))
        if type_matches and entity_overlap:
            correct += 1

    total = len(samples)
    return {
        "sample_count": total,
        "correct": correct,
        "missed": missed,
        "accuracy_percent": round(100.0 * correct / total, 1) if total else 0.0,
    }


def mean_lead_time_seconds(events: list[RiskEvent]) -> float | None:
    """Mean signal detection lead time across events that carry a
    `published_at` timestamp (Phase 11 Evaluation Metrics table)."""
    lead_times = [
        (event.detected_at - event.published_at).total_seconds()
        for event in events
        if event.published_at is not None
    ]
    return round(sum(lead_times) / len(lead_times), 1) if lead_times else None


def resolution_rate_percent(events: list[RiskEvent]) -> float:
    """Percentage of events with at least one resolved affected entity -
    the same "80% resolution" checkpoint Phase 4 validated, reusable here
    against any batch of live/seeded events."""
    return percent_matching(events, lambda event: bool(event.affected_entities))
