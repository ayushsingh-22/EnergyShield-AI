from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes import risk as risk_routes
from models.core_schema import CommodityType, RiskEventType, SourceReliability
from models.event_schema import RiskEvent

app = FastAPI()
app.include_router(risk_routes.router)
client = TestClient(app)


def test_get_corridor_risk():
    response = client.get('/api/v1/risk/corridors')

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert payload[0]['entity_type'] in {'CHOKEPOINT', 'SHIPPING_ROUTE'}
    assert 'confidence' in payload[0]
    assert 'assumptions' in payload[0]


def test_get_risk_history_found():
    # Real risk history (unlike the old static mock) only grows when a
    # score actually changes - establish a baseline snapshot, then inject a
    # new high-severity event so a second history entry gets recorded.
    client.get('/api/v1/risk/corridors')
    risk_routes._service.event_service.add_event(
        RiskEvent(
            event_id="EVT-TEST-HORMUZ-SPIKE",
            event_type=RiskEventType.MARITIME_ATTACK,
            commodity_type=CommodityType.CRUDE_OIL,
            title="Test-injected severe incident",
            summary="Synthetic event for history-growth test.",
            detected_at=datetime.now(timezone.utc),
            source_name="test",
            source_reliability=SourceReliability.OFFICIAL,
            affected_entities=["CHK_HORMUZ"],
            severity=5,
            confidence=0.9,
        )
    )

    response = client.get('/api/v1/risk/history/CHK_HORMUZ')

    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 2
    assert history[-1]['entity_id'] == 'CHK_HORMUZ'
    assert history[-1]['risk_score'] > history[0]['risk_score']


def test_get_risk_history_not_found():
    response = client.get('/api/v1/risk/history/UNKNOWN')

    assert response.status_code == 404
