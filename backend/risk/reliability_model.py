"""Source reliability and multi-source corroboration weighting for risk scoring (Phase 5, section 5.4 / plan Risk Formula "Source Reliability Score")."""

from __future__ import annotations

from models.core_schema import SourceReliability
from models.event_schema import RiskEvent

# 0-100 baseline score per reliability tier - an OFFICIAL alert should pull
# a corridor's reliability term far higher than an unconfirmed LOW-tier
# rumor, mirroring Planning Principle #3 ("real-time news is unreliable
# until validated").
_RELIABILITY_BASE_SCORE: dict[str, float] = {
    SourceReliability.OFFICIAL: 100.0,
    SourceReliability.HIGH: 85.0,
    SourceReliability.MEDIUM: 60.0,
    SourceReliability.LOW: 35.0,
    SourceReliability.SIMULATED: 40.0,
}


def compute_source_reliability_score(events: list[RiskEvent]) -> float:
    """0-100 average reliability score across the given events' sources.
    No active events -> 0 (there is nothing to weight)."""
    if not events:
        return 0.0
    scores = [_RELIABILITY_BASE_SCORE.get(event.source_reliability, 50.0) for event in events]
    return round(sum(scores) / len(scores), 2)


def compute_corroboration_bonus(events: list[RiskEvent]) -> float:
    """0-15 bonus for multiple independent sources reporting on the same
    entity ("multiple independent sources increase confidence" - plan
    section 4.4, reused here since the same corroboration signal applies
    to risk scoring)."""
    distinct_sources = {event.source_name for event in events}
    if len(distinct_sources) <= 1:
        return 0.0
    return round(min(15.0, (len(distinct_sources) - 1) * 7.5), 2)
