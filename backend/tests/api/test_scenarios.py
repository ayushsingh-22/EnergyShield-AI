from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes import scenarios as scenarios_routes

app = FastAPI()
app.include_router(scenarios_routes.router)
client = TestClient(app)

REQUEST = {
    'scenario_type': 'HORMUZ_PARTIAL_CLOSURE',
    'commodity_type': 'CRUDE_OIL',
    'duration_days': 14,
    'severity': 'HIGH',
    'affected_entities': ['CHK_HORMUZ'],
    'manual_overrides': {},
}


def test_run_scenario_and_fetch_by_id():
    run_response = client.post('/api/v1/scenarios/run', json=REQUEST)

    assert run_response.status_code == 200
    scenario = run_response.json()
    assert scenario['scenario_id']
    assert scenario['recommended_action_required'] is True

    get_response = client.get(f"/api/v1/scenarios/{scenario['scenario_id']}")

    assert get_response.status_code == 200
    assert get_response.json()['scenario_id'] == scenario['scenario_id']


def test_get_scenario_not_found():
    response = client.get('/api/v1/scenarios/UNKNOWN')

    assert response.status_code == 404
