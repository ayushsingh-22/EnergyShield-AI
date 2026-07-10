from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes import recommendations as recommendation_routes
from api.routes import scenarios as scenarios_routes

app = FastAPI()
app.include_router(scenarios_routes.router)
app.include_router(recommendation_routes.router)
client = TestClient(app)

REQUEST = {
    'scenario_type': 'HORMUZ_PARTIAL_CLOSURE',
    'commodity_type': 'CRUDE_OIL',
    'duration_days': 10,
    'severity': 'SEVERE',
}


def test_get_recommendation_for_existing_scenario():
    scenario = client.post('/api/v1/scenarios/run', json=REQUEST).json()

    response = client.get(f"/api/v1/recommendations/{scenario['scenario_id']}")

    assert response.status_code == 200
    payload = response.json()
    assert payload['scenario_id'] == scenario['scenario_id']
    assert payload['ranked_options']
    assert 'spr_plan' in payload


def test_get_recommendation_missing_scenario():
    response = client.get('/api/v1/recommendations/UNKNOWN')

    assert response.status_code == 404
