from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes import events as events_routes

app = FastAPI()
app.include_router(events_routes.router)
client = TestClient(app)


def test_get_latest_events_returns_seeded_pipeline_output():
    response = client.get("/api/v1/events/latest")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # The maritime_alerts, sanctions, and commodity_prices seeded records
    # are OFFICIAL/HIGH reliability, so they always classify deterministically
    # via the official_alert_direct path regardless of LLM availability.
    assert len(data) > 0
    assert "event_id" in data[0]
    assert "event_type" in data[0]
    assert "severity" in data[0]
    assert "confidence" in data[0]


def test_get_latest_events_respects_limit():
    response = client.get("/api/v1/events/latest?limit=1")

    assert response.status_code == 200
    assert len(response.json()) <= 1


def test_get_event_found():
    latest = client.get("/api/v1/events/latest").json()
    assert latest, "pipeline bootstrap should have produced at least one event"
    event_id = latest[0]["event_id"]

    response = client.get(f"/api/v1/events/{event_id}")

    assert response.status_code == 200
    assert response.json()["event_id"] == event_id


def test_get_event_not_found():
    response = client.get("/api/v1/events/UNKNOWN_EVENT_ID")

    assert response.status_code == 404


def test_run_extraction_pipeline_is_idempotent_on_repeated_runs():
    """Re-running the pipeline (e.g. from a future Phase 10 scheduler) must
    refresh the event store, not accumulate duplicates from the same
    seeded collector content forever."""
    first_run_count = len(events_routes.run_extraction_pipeline())
    second_run_count = len(events_routes.run_extraction_pipeline())

    assert second_run_count == first_run_count
    assert events_routes._event_service.count() == second_run_count
