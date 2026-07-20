"""Captures analyst feedback on recommendations: usefulness, accepted/rejected/modified action, and rejection reason (Phase 13, section 13.6)."""

from __future__ import annotations

from datetime import datetime, timezone
from itertools import count

from models.learning_schema import FeedbackAction, FeedbackEntry

_counter = count(1)


class FeedbackService:
    """In-memory analyst feedback store (section 13.6). Every entry is
    linked to a `recommendation_id` so the audit trail and future label
    building can trace exactly which recommendation an analyst accepted,
    rejected, or modified, and why."""

    def __init__(self) -> None:
        self._feedback: dict[str, list[FeedbackEntry]] = {}

    def submit_feedback(
        self,
        *,
        recommendation_id: str,
        useful: bool,
        action_taken: FeedbackAction,
        rejection_reason: str | None = None,
        submitted_by: str | None = None,
    ) -> FeedbackEntry:
        entry = FeedbackEntry(
            feedback_id=f"FB-{next(_counter):06d}",
            recommendation_id=recommendation_id,
            useful=useful,
            action_taken=action_taken,
            rejection_reason=rejection_reason,
            submitted_by=submitted_by,
            submitted_at=datetime.now(timezone.utc),
        )
        self._feedback.setdefault(recommendation_id, []).append(entry)
        return entry

    def get_for_recommendation(self, recommendation_id: str) -> list[FeedbackEntry]:
        return list(self._feedback.get(recommendation_id, []))

    def usefulness_rate_percent(self) -> float:
        """"Recommendation usefulness" evaluation metric (docs/CONTINUOUS_LEARNING.md):
        share of all feedback marked useful."""
        all_entries = [entry for entries in self._feedback.values() for entry in entries]
        if not all_entries:
            return 0.0
        useful_count = sum(1 for entry in all_entries if entry.useful)
        return round(100.0 * useful_count / len(all_entries), 1)


_default_service: FeedbackService | None = None


def get_feedback_service() -> FeedbackService:
    """Returns the process-wide `FeedbackService` singleton."""
    global _default_service
    if _default_service is None:
        _default_service = FeedbackService()
    return _default_service
