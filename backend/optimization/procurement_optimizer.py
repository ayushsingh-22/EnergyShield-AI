"""Ranks alternate supplier/route procurement options using cost, safety, reliability, delivery time, and compatibility."""

from __future__ import annotations

from graph import graph_queries
from models.core_schema import ActionPriority, RiskLevel
from models.digital_twin_schema import ShippingRoute, SupplierCountry
from models.recommendation_schema import ProcurementOption
from optimization import route_ranker
from services.digital_twin_service import DigitalTwinService


def find_blocked_suppliers(digital_twin: DigitalTwinService, resolved_entity_ids: list[str]) -> list[str]:
    """Suppliers the scenario names directly, plus suppliers whose default
    route transits a chokepoint the scenario resolved to (section 7.1,
    step 1: link the disrupted supplier/route to the scenario)."""
    blocked = {entity_id for entity_id in resolved_entity_ids if entity_id.startswith("SUP_")}
    chokepoint_ids = {entity_id for entity_id in resolved_entity_ids if entity_id.startswith("CHK_")}
    if chokepoint_ids:
        for supplier in digital_twin.get_suppliers():
            route = digital_twin.routes.get(supplier.default_shipping_route_id)
            if route and chokepoint_ids.intersection(route.affected_chokepoint_ids):
                blocked.add(supplier.id)
    return sorted(blocked)


def find_candidate_suppliers(
    digital_twin: DigitalTwinService,
    commodity: str,
    blocked_supplier_ids: list[str],
    high_risk_affected_entities: set[str] | None = None,
) -> list[SupplierCountry]:
    """Graph-derived alternative suppliers (section 7.1, steps 1-2), falling
    back to the same digital-twin data `graph.graph_queries.get_alternative_suppliers`
    would traverse when no live graph is available - the same
    graceful-degradation pattern `risk/exposure_model.py` already uses.
    Suppliers currently named in a high-severity risk event are excluded
    either way (step 2: "exclude suppliers affected by active high-risk events")."""
    high_risk_affected_entities = high_risk_affected_entities or set()

    graph_candidate_ids: set[str] = set()
    for blocked_id in blocked_supplier_ids or [""]:
        for row in graph_queries.get_alternative_suppliers(commodity, blocked_id):
            entity_id = row.get("entity_id")
            if entity_id:
                graph_candidate_ids.add(entity_id)

    candidate_ids = graph_candidate_ids or {
        supplier.id for supplier in digital_twin.get_suppliers() if supplier.id not in blocked_supplier_ids
    }
    candidate_ids -= set(blocked_supplier_ids)
    candidate_ids -= high_risk_affected_entities

    candidates = [digital_twin.find_supplier(supplier_id) for supplier_id in candidate_ids]
    return sorted(
        (candidate for candidate in candidates if candidate is not None),
        key=lambda supplier: supplier.import_share_percent,
        reverse=True,
    )


def _supplier_reliability_score(supplier: SupplierCountry) -> float:
    """Higher baseline import share indicates an already-proven, higher-volume
    supplier relationship (section 7.1, step 3: "score suppliers by reliability")."""
    return round(min(1.0, 0.5 + (supplier.import_share_percent / 100)), 2)


def _refinery_compatibility_score(digital_twin: DigitalTwinService, route: ShippingRoute | None) -> float:
    """1.0 when the route's destination port already feeds at least one
    refinery (an existing, presumably grade-compatible connection); a
    neutral score when there's no route to judge compatibility from."""
    if route is None:
        return 0.5
    connected = any(
        route.destination_port_id in refinery.connected_import_port_ids
        for refinery in digital_twin.get_refineries()
    )
    return 0.8 if connected else 0.5


def score_option(
    digital_twin: DigitalTwinService,
    supplier: SupplierCountry,
    route: ShippingRoute | None,
    freight_cost_impact_percent: float,
) -> dict[str, float]:
    """Procurement Scoring Formula (Phase 7): 0.25 cost efficiency + 0.25
    route safety + 0.20 supplier reliability + 0.15 delivery time + 0.15
    refinery compatibility."""
    cost = route_ranker.score_cost_efficiency(route, freight_cost_impact_percent)
    safety = route_ranker.score_route_safety(route)
    reliability = _supplier_reliability_score(supplier)
    delivery = route_ranker.score_delivery_time(route)
    compatibility = _refinery_compatibility_score(digital_twin, route)
    composite = round(
        0.25 * cost + 0.25 * safety + 0.20 * reliability + 0.15 * delivery + 0.15 * compatibility, 2
    )
    return {
        "cost": cost,
        "safety": safety,
        "reliability": reliability,
        "delivery": delivery,
        "compatibility": compatibility,
        "composite": composite,
    }


def rank_procurement_options(
    digital_twin: DigitalTwinService,
    candidates: list[SupplierCountry],
    freight_cost_impact_percent: float,
    action_required: bool,
    max_options: int = 3,
) -> list[ProcurementOption]:
    """Converts scored candidates into a ranked, user-facing action plan
    (section 7.4)."""
    scored = []
    for supplier in candidates:
        route = (
            digital_twin.routes.get(supplier.default_shipping_route_id)
            if supplier.default_shipping_route_id
            else None
        )
        breakdown = score_option(digital_twin, supplier, route, freight_cost_impact_percent)
        scored.append((supplier, route, breakdown))
    scored.sort(key=lambda item: item[2]["composite"], reverse=True)

    options: list[ProcurementOption] = []
    for rank, (supplier, route, breakdown) in enumerate(scored[:max_options], start=1):
        risk_level = route.risk_level if route is not None else RiskLevel.MEDIUM
        if rank == 1 and action_required:
            priority = ActionPriority.IMMEDIATE
        elif breakdown["composite"] >= 0.55:
            priority = ActionPriority.CONTINGENCY
        else:
            priority = ActionPriority.MONITOR

        options.append(
            ProcurementOption(
                rank=rank,
                supplier=supplier.name,
                route=route.name if route is not None else "No default route on record for this supplier",
                estimated_delay_days=(
                    route.estimated_transit_days
                    if route is not None and route.estimated_transit_days is not None
                    else 10.0
                ),
                cost_impact_percent=round(freight_cost_impact_percent * (1.0 - breakdown["cost"]), 1),
                risk_level=risk_level,
                feasibility_score=breakdown["composite"],
                reason=(
                    f"Digital-twin/graph-ranked option: cost {breakdown['cost']}, route safety "
                    f"{breakdown['safety']}, supplier reliability {breakdown['reliability']}, delivery "
                    f"time {breakdown['delivery']}, refinery compatibility {breakdown['compatibility']} "
                    "(Phase 7 procurement scoring formula)."
                ),
                action_priority=priority,
            )
        )
    return options
