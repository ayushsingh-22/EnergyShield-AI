from services.audit_service import AuditService


def test_record_and_retrieve_events_for_entity():
    service = AuditService()
    service.record_event(entity_id="SCN-1", entity_type="SCENARIO", action="SCENARIO_RUN", summary="ran it")
    service.record_event(entity_id="SCN-1", entity_type="SCENARIO", action="SCENARIO_RUN", summary="ran it again")
    service.record_event(entity_id="SCN-2", entity_type="SCENARIO", action="SCENARIO_RUN", summary="other scenario")

    events = service.get_events_for_entity("SCN-1")

    assert len(events) == 2
    assert all(event.entity_id == "SCN-1" for event in events)
    assert events[0].audit_id != events[1].audit_id


def test_unknown_entity_returns_empty_list():
    service = AuditService()
    assert service.get_events_for_entity("UNKNOWN") == []
