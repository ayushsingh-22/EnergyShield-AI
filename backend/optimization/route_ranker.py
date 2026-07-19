"""Scores route options by cost, delay, risk, and port feasibility (Phase 7, section 7.2)."""

from __future__ import annotations

from models.core_schema import RiskLevel
from models.digital_twin_schema import ShippingRoute

_RISK_LEVEL_SCORE: dict[RiskLevel, float] = {
    RiskLevel.LOW: 1.0,
    RiskLevel.MEDIUM: 0.7,
    RiskLevel.HIGH: 0.4,
    RiskLevel.SEVERE: 0.2,
    RiskLevel.CRITICAL: 0.05,
}


def score_cost_efficiency(route: ShippingRoute | None, freight_cost_impact_percent: float) -> float:
    """Higher is better: a shorter route under lower scenario freight-cost
    pressure is cheaper to substitute onto."""
    if route is None:
        return 0.4
    distance_penalty = min((route.distance_km or 0) / 20000, 0.5)
    cost_penalty = min(max(freight_cost_impact_percent, 0.0) / 200, 0.5)
    return round(max(0.0, 1.0 - distance_penalty - cost_penalty), 2)


def score_route_safety(route: ShippingRoute | None) -> float:
    """Derived from the route's own `risk_level`, which Phase 5's
    `risk_graph_updater` keeps current on the knowledge graph node."""
    if route is None:
        return 0.5
    return _RISK_LEVEL_SCORE.get(route.risk_level, 0.5)


def score_delivery_time(route: ShippingRoute | None) -> float:
    if route is None or route.estimated_transit_days is None:
        return 0.4
    return round(max(0.0, 1.0 - min(route.estimated_transit_days / 30, 0.9)), 2)


def score_route(route: ShippingRoute | None, freight_cost_impact_percent: float) -> dict[str, float]:
    """Standalone route-only score (cost/safety/delivery equally weighted),
    for ranking routes independent of any particular supplier.
    `procurement_optimizer` instead combines these three components with
    supplier reliability and refinery compatibility per the full Phase 7
    scoring formula."""
    cost = score_cost_efficiency(route, freight_cost_impact_percent)
    safety = score_route_safety(route)
    delivery = score_delivery_time(route)
    return {
        "cost": cost,
        "safety": safety,
        "delivery": delivery,
        "composite": round((cost + safety + delivery) / 3, 2),
    }


def rank_routes(routes: list[ShippingRoute], freight_cost_impact_percent: float) -> list[dict]:
    """Ranks candidate routes best-first (section 7.2, steps 2-3)."""
    scored = [{"route": route, **score_route(route, freight_cost_impact_percent)} for route in routes]
    return sorted(scored, key=lambda item: item["composite"], reverse=True)
