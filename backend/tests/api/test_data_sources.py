from fastapi.testclient import TestClient
from api.routes.data_sources import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_get_data_freshness():
    response = client.get("/api/v1/data/freshness")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "source_name" in data[0]

def test_get_data_sources():
    response = client.get("/api/v1/data/sources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "source_name" in data[0]
    assert "url" in data[0]

def test_get_data_health():
    response = client.get("/api/v1/data/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["active_sources"] > 0
