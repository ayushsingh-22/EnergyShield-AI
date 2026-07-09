from fastapi.testclient import TestClient
from api.routes.digital_twin import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_get_map():
    response = client.get("/api/v1/digital-twin/map")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    # Should have some features loaded from seeds
    assert len(data["features"]) > 0

def test_get_suppliers():
    response = client.get("/api/v1/digital-twin/suppliers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "entity_id" in data[0]

def test_get_exposure():
    response = client.get("/api/v1/digital-twin/exposure")
    assert response.status_code == 200
    data = response.json()
    assert "total_supplier_exposure_percent" in data

def test_get_entity_found():
    response = client.get("/api/v1/digital-twin/entity/SUP_IRQ")
    assert response.status_code == 200
    assert response.json()["entity_id"] == "SUP_IRQ"

def test_get_entity_not_found():
    response = client.get("/api/v1/digital-twin/entity/UNKNOWN_ID")
    assert response.status_code == 404
