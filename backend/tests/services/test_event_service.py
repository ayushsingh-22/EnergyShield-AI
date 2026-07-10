from datetime import datetime, timedelta, timezone

from models.core_schema import CommodityType, RiskEventType, SourceReliability
from models.event_schema import RiskEvent
from services.event_service import EventService


def _event(event_id, detected_at):
    return RiskEvent(
        event_id=event_id,
        event_type=RiskEventType.MARITIME_ATTACK,
        commodity_type=CommodityType.CRUDE_OIL,
        title="t",
        summary="s",
        detected_at=detected_at,
        source_name="gdelt",
        source_reliability=SourceReliability.MEDIUM,
        severity=3,
        confidence=0.5,
    )


def test_add_and_get_event():
    service = EventService()
    event = _event("EVT-1", datetime.now(timezone.utc))

    service.add_event(event)

    assert service.get_event("EVT-1") is event
    assert service.count() == 1


def test_get_latest_orders_by_detected_at_desc():
    service = EventService()
    now = datetime.now(timezone.utc)
    older = _event("EVT-OLD", now - timedelta(hours=1))
    newer = _event("EVT-NEW", now)

    service.add_events([older, newer])
    latest = service.get_latest(limit=10)

    assert [event.event_id for event in latest] == ["EVT-NEW", "EVT-OLD"]


def test_get_latest_respects_limit():
    service = EventService()
    now = datetime.now(timezone.utc)
    service.add_events([_event(f"EVT-{i}", now - timedelta(minutes=i)) for i in range(5)])

    assert len(service.get_latest(limit=2)) == 2


def test_get_event_missing_returns_none():
    service = EventService()
    assert service.get_event("MISSING") is None


def test_add_event_overwrites_same_id():
    service = EventService()
    now = datetime.now(timezone.utc)
    service.add_event(_event("EVT-1", now))
    service.add_event(_event("EVT-1", now + timedelta(minutes=5)))

    assert service.count() == 1


def test_replace_all_clears_previous_events():
    """A pipeline re-run must refresh state, not accumulate duplicates
    forever (Phase 4 idempotency fix)."""
    service = EventService()
    now = datetime.now(timezone.utc)
    service.add_events([_event("EVT-OLD-1", now), _event("EVT-OLD-2", now)])

    service.replace_all([_event("EVT-NEW-1", now)])

    assert service.count() == 1
    assert service.get_event("EVT-OLD-1") is None
    assert service.get_event("EVT-NEW-1") is not None
