"""Main risk score computation combining event severity, source
reliability, import exposure, anomaly signals, and price movement into a
single 0-100 `RiskScore` per corridor/supplier/refinery entity (Phase 5,
sections 5.1-5.3).

Initial Risk Formula (plan Phase 5):
    risk_score =
        0.30 * event_severity_score
      + 0.20 * source_reliability_score
      + 0.20 * import_exposure_score
      + 0.15 * anomaly_score
      + 0.15 * commodity_price_movement_score

The 0.15-weighted "anomaly" term uses a different underlying signal per
entity type, since the plan's own per-entity processing steps (5.1 vs 5.2)
call for different stress signals: AIS/route anomaly for corridors and
refineries (section 5.1, step 4), sanctions score for suppliers (section
5.2, step 2 - a supplier country has no vessel movements of its own for an
AIS anomaly to apply to).
"""

from __future__ import annotations

from datetime import datetime, timezone

from models.core_schema import Assumption, CommodityType, EntityType, RiskLevel
from models.event_schema import RiskEvent
from models.risk_schema import RiskScore
from risk import anomaly_model, exposure_model, reliability_model
from services.digital_twin_service import DigitalTwinService

# Short, non-technical descriptions per event type (plan Phase 5
# validation: "Top drivers are understandable to a non-technical user").
_EVENT_TYPE_DRIVER_TEXT: dict[str, str] = {
    "MARITIME_ATTACK": "Maritime security incident reported in this corridor",
    "PORT_CLOSURE": "Port closure reported",
    "SANCTION_UPDATE": "Active sanctions affecting this entity",
    "OPEC_SUPPLY_CUT": "OPEC+ supply cut announced",
    "PRICE_SPIKE": "Recent crude price spike",
    "AIS_REROUTING": "Vessel rerouting/AIS anomaly detected",
    "CHOKEPOINT_CONGESTION": "Chokepoint congestion reported",
    "REFINERY_SUPPLY_RISK": "Refinery supply risk reported",
    "EXPORT_RESTRICTION": "Export restriction in effect",
    "WEATHER_DISRUPTION": "Weather-related disruption reported",
    "POLITICAL_INSTABILITY": "Political instability reported",
}


def _events_affecting(events: list[RiskEvent], entity_id: str) -> list[RiskEvent]:
    """Groups active events by corridor/supplier/refinery (plan section
    5.1, step 1)."""
    return [event for event in events if entity_id in (event.affected_entities or [])]


def _dedupe_events(events: list[RiskEvent]) -> list[RiskEvent]:
    seen: set[str] = set()
    result: list[RiskEvent] = []
    for event in events:
        if event.event_id not in seen:
            seen.add(event.event_id)
            result.append(event)
    return result


def _severity_score(events: list[RiskEvent]) -> float:
    """Severity-weighted event score (plan section 5.1, step 2): dominated
    by the worst active event, nudged up when several events are active
    concurrently."""
    if not events:
        return 0.0
    max_severity = max(event.severity for event in events)
    count_bonus = min(10.0, (len(events) - 1) * 2.5)
    return round(min(100.0, max_severity * 20 + count_bonus), 2)


def _risk_level(score: float) -> RiskLevel:
    if score >= 80:
        return RiskLevel.CRITICAL
    if score >= 60:
        return RiskLevel.SEVERE
    if score >= 40:
        return RiskLevel.HIGH
    if score >= 20:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _compute_confidence(events: list[RiskEvent], has_exposure_data: bool) -> float:
    if not events:
        # No live evidence - confidence rests on structural exposure data alone.
        return 0.55 if has_exposure_data else 0.35
    average_event_confidence = sum(event.confidence for event in events) / len(events)
    return round(min(0.95, max(0.4, average_event_confidence)), 2)


def _build_top_drivers(
    events: list[RiskEvent],
    exposure_score: float,
    anomaly_score: float,
    anomaly_driver_text: str,
    price_score: float,
) -> list[str]:
    drivers: list[str] = []
    high_severity_types = {event.event_type for event in events if event.severity >= 4}
    for event_type in high_severity_types:
        drivers.append(f"High-severity event: {_EVENT_TYPE_DRIVER_TEXT.get(event_type, str(event_type))}")

    other_types = {event.event_type for event in events} - high_severity_types
    for event_type in other_types:
        drivers.append(_EVENT_TYPE_DRIVER_TEXT.get(event_type, str(event_type)))

    if exposure_score >= 25:
        drivers.append(f"High India crude import exposure via this entity ({exposure_score:.1f}% of imports)")
    if anomaly_score > 0:
        drivers.append(anomaly_driver_text)
    if price_score > 0:
        drivers.append("Market-wide crude price movement adds pressure")
    if len({event.source_name for event in events}) > 1:
        drivers.append("Corroborated by multiple independent sources")

    if not drivers:
        drivers.append("No active risk events; score reflects baseline import exposure only")

    return drivers[:5]


class RiskScoringEngine:
    """Computes live `RiskScore` records for corridors (chokepoints and
    routes), suppliers, and refineries from the current set of extracted
    `RiskEvent`s plus Phase 2 digital-twin exposure data."""

    def __init__(self, digital_twin: DigitalTwinService | None = None):
        self.digital_twin = digital_twin or _load_default_digital_twin()

    def _score_entity(
        self,
        entity_id: str,
        entity_type: EntityType,
        events: list[RiskEvent],
        exposure_score: float,
        anomaly_score: float,
        anomaly_driver_text: str,
        price_score: float,
    ) -> RiskScore:
        severity_score = _severity_score(events)
        reliability_score = min(
            100.0,
            reliability_model.compute_source_reliability_score(events)
            + reliability_model.compute_corroboration_bonus(events),
        )

        risk_score = round(
            max(
                0.0,
                min(
                    100.0,
                    0.30 * severity_score
                    + 0.20 * reliability_score
                    + 0.20 * exposure_score
                    + 0.15 * anomaly_score
                    + 0.15 * price_score,
                ),
            ),
            1,
        )

        return RiskScore(
            entity_id=entity_id,
            entity_type=entity_type,
            commodity_type=CommodityType.CRUDE_OIL,
            risk_score=risk_score,
            risk_level=_risk_level(risk_score),
            top_drivers=_build_top_drivers(events, exposure_score, anomaly_score, anomaly_driver_text, price_score),
            evidence_event_ids=[event.event_id for event in events],
            confidence=_compute_confidence(events, has_exposure_data=exposure_score > 0),
            assumptions=[
                Assumption(
                    # Not "pending Phase 11" - explainability (Phase 11) and
                    # threshold calibration (Phase 13's
                    # learning.model_trainer.calibrate_flag_threshold) both
                    # exist. The honest caveat is that calibration is a
                    # grid-search over the small seeded historical case set
                    # (learning/disruption_case_library.py), not a trained
                    # statistical model - a data-volume limitation, not a
                    # missing feature.
                    description=(
                        "Risk formula weights (0.30/0.20/0.20/0.15/0.15) are analyst-set starting "
                        "values; automated calibration exists but is only as good as the small "
                        "seeded historical case set it grid-searches against."
                    ),
                    is_simulated=True,
                )
            ],
            audit_id=f"AUD-RISK-{entity_id}",
            updated_at=datetime.now(timezone.utc),
        )

    def score_corridors(self, events: list[RiskEvent]) -> list[RiskScore]:
        price_score = anomaly_model.compute_price_movement_score(events)
        anomaly_driver_text = "Vessel rerouting/AIS anomaly detected nearby"
        scores = []
        for chokepoint in self.digital_twin.get_chokepoints():
            entity_events = _events_affecting(events, chokepoint.id)
            exposure_score = exposure_model.compute_chokepoint_exposure_score(self.digital_twin, chokepoint.id)
            anomaly_score = anomaly_model.compute_ais_anomaly_score(entity_events)
            scores.append(
                self._score_entity(
                    chokepoint.id,
                    EntityType.CHOKEPOINT,
                    entity_events,
                    exposure_score,
                    anomaly_score,
                    anomaly_driver_text,
                    price_score,
                )
            )
        for route in self.digital_twin.get_routes():
            entity_events = _events_affecting(events, route.id)
            exposure_score = exposure_model.compute_route_exposure_score(self.digital_twin, route.id)
            anomaly_score = anomaly_model.compute_ais_anomaly_score(entity_events)
            scores.append(
                self._score_entity(
                    route.id,
                    EntityType.SHIPPING_ROUTE,
                    entity_events,
                    exposure_score,
                    anomaly_score,
                    anomaly_driver_text,
                    price_score,
                )
            )
        return scores

    def score_suppliers(self, events: list[RiskEvent]) -> list[RiskScore]:
        price_score = anomaly_model.compute_price_movement_score(events)
        # Suppliers don't have vessel movements of their own, so the
        # formula's anomaly-like term is a sanctions score instead of the
        # AIS/route anomaly score corridors use (plan section 5.2, step 2:
        # "add sanctions score").
        anomaly_driver_text = "Active sanctions pressure on this supplier"
        scores = []
        for supplier in self.digital_twin.get_suppliers():
            direct_events = _events_affecting(events, supplier.id)
            route_events = (
                _events_affecting(events, supplier.default_shipping_route_id)
                if supplier.default_shipping_route_id
                else []
            )
            entity_events = _dedupe_events(direct_events + route_events)
            exposure_score = exposure_model.compute_supplier_exposure_score(self.digital_twin, supplier.id)
            sanctions_score = anomaly_model.compute_sanctions_score(entity_events)
            scores.append(
                self._score_entity(
                    supplier.id,
                    EntityType.SUPPLIER_COUNTRY,
                    entity_events,
                    exposure_score,
                    sanctions_score,
                    anomaly_driver_text,
                    price_score,
                )
            )
        return scores

    def score_refineries(self, events: list[RiskEvent]) -> list[RiskScore]:
        price_score = anomaly_model.compute_price_movement_score(events)
        anomaly_driver_text = "Vessel rerouting/AIS anomaly detected nearby"
        refinery_events: dict[str, list[RiskEvent]] = {}
        refinery_exposure: dict[str, float] = {}

        for chokepoint in self.digital_twin.get_chokepoints():
            chokepoint_events = _events_affecting(events, chokepoint.id)
            if not chokepoint_events:
                continue
            for exposed in exposure_model.get_exposed_refineries(self.digital_twin, chokepoint.id):
                refinery_id = exposed["refinery_id"]
                refinery_exposure[refinery_id] = max(
                    refinery_exposure.get(refinery_id, 0.0), exposed["capacity_weight_percent"]
                )
                refinery_events.setdefault(refinery_id, []).extend(chokepoint_events)

        scores = []
        for refinery in self.digital_twin.get_refineries():
            entity_events = _dedupe_events(refinery_events.get(refinery.id, []))
            exposure_score = refinery_exposure.get(refinery.id, 0.0)
            anomaly_score = anomaly_model.compute_ais_anomaly_score(entity_events)
            scores.append(
                self._score_entity(
                    refinery.id,
                    EntityType.REFINERY,
                    entity_events,
                    exposure_score,
                    anomaly_score,
                    anomaly_driver_text,
                    price_score,
                )
            )
        return scores

    def score_all(self, events: list[RiskEvent]) -> list[RiskScore]:
        return self.score_corridors(events) + self.score_suppliers(events) + self.score_refineries(events)


_default_digital_twin: DigitalTwinService | None = None


def _load_default_digital_twin() -> DigitalTwinService:
    global _default_digital_twin
    if _default_digital_twin is None:
        service = DigitalTwinService()
        service.load_seed_data()
        _default_digital_twin = service
    return _default_digital_twin
