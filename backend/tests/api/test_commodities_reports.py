from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes import commodities as commodities_routes
from api.routes import recommendations as recommendation_routes
from api.routes import reports as reports_routes
from api.routes import scenarios as scenarios_routes

app = FastAPI()
app.include_router(scenarios_routes.router)
app.include_router(recommendation_routes.router)
app.include_router(reports_routes.router)
app.include_router(commodities_routes.router)
client = TestClient(app)


def test_list_commodities():
    response = client.get('/api/v1/commodities')

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert payload[0]['commodity_type']


def test_run_commodity_scenario_and_get_report():
    scenario_response = client.post(
        '/api/v1/commodities/CRUDE_OIL/scenarios/run',
        json={
            'scenario_type': 'HORMUZ_PARTIAL_CLOSURE',
            'commodity_type': 'LNG',
            'duration_days': 7,
            'severity': 'HIGH',
        },
    )
    assert scenario_response.status_code == 200
    scenario = scenario_response.json()
    assert scenario['commodity_type'] == 'CRUDE_OIL'

    report_response = client.post('/api/v1/reports/generate', json={'scenario_id': scenario['scenario_id']})

    assert report_response.status_code == 200
    report = report_response.json()
    assert report['scenario_id'] == scenario['scenario_id']
    assert report['recommendation_id']
