"""AIS rerouting and commodity price anomaly features used by the risk scoring engine (Phase 5, Risk Formula "Route or AIS Anomaly Score" and "Commodity Price Movement Score")."""

from __future__ import annotations

from models.core_schema import RiskEventType
from models.event_schema import RiskEvent


def compute_ais_anomaly_score(events: list[RiskEvent]) -> float:
    """0-100: severity of any AIS_REROUTING or CHOKEPOINT_CONGESTION event
    among the given events - the "Route or AIS Anomaly Score" term. No
    matching event -> 0."""
    anomaly_events = [
        event
        for event in events
        if event.event_type in (RiskEventType.AIS_REROUTING, RiskEventType.CHOKEPOINT_CONGESTION)
    ]
    if not anomaly_events:
        return 0.0
    return round(min(100.0, max(event.severity for event in anomaly_events) * 20), 2)


def compute_sanctions_score(events: list[RiskEvent]) -> float:
    """0-100: severity of any SANCTION_UPDATE event among the given events
    - plan section 5.2, step 2: "add sanctions score." This is the
    supplier-side analog of `compute_ais_anomaly_score`: an AIS/route
    anomaly is a meaningful stress signal for a corridor, but a supplier
    *country* doesn't have vessel movements of its own - an active
    sanctions action is the equivalent signal, so
    `RiskScoringEngine.score_suppliers` uses this in place of the AIS term
    `score_corridors` uses."""
    sanction_events = [event for event in events if event.event_type == RiskEventType.SANCTION_UPDATE]
    if not sanction_events:
        return 0.0
    return round(min(100.0, max(event.severity for event in sanction_events) * 20), 2)


def compute_price_movement_score(events: list[RiskEvent]) -> float:
    """0-100: severity of any PRICE_SPIKE event across the given events -
    the "Commodity Price Movement Score" term. Unlike the other terms this
    is intentionally computed over the *global* active event set rather
    than one entity's events, since a price spike is a market-wide signal
    (the commodity price collector has no specific corridor/supplier to
    attach it to) that should apply uniform pressure to every corridor and
    supplier's score rather than only the one entity a price event happens
    to resolve against."""
    price_events = [event for event in events if event.event_type == RiskEventType.PRICE_SPIKE]
    if not price_events:
        return 0.0
    return round(min(100.0, max(event.severity for event in price_events) * 20), 2)
