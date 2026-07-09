from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes import graph as graph_routes

app = FastAPI()
app.include_router(graph_routes.router)
client = TestClient(app)


def test_get_entity_found(monkeypatch):
    monkeypatch.setattr(
        graph_routes.graph_queries,
        "get_entity_neighborhood",
        lambda entity_id: {
            "nodes": [{"entity_id": entity_id, "label": "Refinery", "properties": {}}],
            "edges": [],
            "query_description": "ok",
        },
    )

    response = client.get("/api/v1/graph/entity/REF_JAM")

    assert response.status_code == 200
    assert response.json()["nodes"][0]["entity_id"] == "REF_JAM"


def test_get_entity_not_found(monkeypatch):
    monkeypatch.setattr(
        graph_routes.graph_queries,
        "get_entity_neighborhood",
        lambda entity_id: {"nodes": [], "edges": [], "query_description": "not found"},
    )

    response = client.get("/api/v1/graph/entity/UNKNOWN")

    assert response.status_code == 404


def test_get_refineries_exposed(monkeypatch):
    monkeypatch.setattr(
        graph_routes.graph_queries,
        "get_refineries_exposed_to_chokepoint",
        lambda chokepoint_id: [{"entity_id": "REF_JAM", "name": "Reliance Jamnagar"}],
    )

    response = client.get("/api/v1/graph/refineries-exposed?chokepoint_id=CHK_HORMUZ")

    assert response.status_code == 200
    assert response.json() == [{"entity_id": "REF_JAM", "name": "Reliance Jamnagar"}]


def test_get_alternative_suppliers(monkeypatch):
    captured = {}

    def _fake(commodity, blocked_supplier_id):
        captured["commodity"] = commodity
        captured["blocked_supplier_id"] = blocked_supplier_id
        return [{"entity_id": "SUP_KSA"}]

    monkeypatch.setattr(graph_routes.graph_queries, "get_alternative_suppliers", _fake)

    response = client.get("/api/v1/graph/alternative-suppliers?supplier_id=SUP_IRQ&commodity=CRUDE_OIL")

    assert response.status_code == 200
    assert captured == {"commodity": "CRUDE_OIL", "blocked_supplier_id": "SUP_IRQ"}


def test_get_routes_for_supplier(monkeypatch):
    monkeypatch.setattr(
        graph_routes.graph_queries,
        "get_routes_for_supplier",
        lambda supplier_id: [{"entity_id": "RT_BAS_JAM"}],
    )

    response = client.get("/api/v1/graph/routes?supplier_id=SUP_IRQ")

    assert response.status_code == 200
    assert response.json() == [{"entity_id": "RT_BAS_JAM"}]


def test_query_impact(monkeypatch):
    monkeypatch.setattr(
        graph_routes.graph_queries,
        "get_impact_subgraph",
        lambda entity_id, max_hops: {
            "nodes": [{"entity_id": entity_id, "label": "Chokepoint", "properties": {}}],
            "edges": [],
            "query_description": f"impact of {entity_id}",
        },
    )

    response = client.post("/api/v1/graph/query-impact", json={"entity_id": "CHK_HORMUZ", "max_hops": 3})

    assert response.status_code == 200
    assert response.json()["nodes"][0]["entity_id"] == "CHK_HORMUZ"


def test_query_impact_defaults_max_hops(monkeypatch):
    captured = {}

    def _fake(entity_id, max_hops):
        captured["max_hops"] = max_hops
        return {"nodes": [], "edges": [], "query_description": "x"}

    monkeypatch.setattr(graph_routes.graph_queries, "get_impact_subgraph", _fake)

    response = client.post("/api/v1/graph/query-impact", json={"entity_id": "CHK_HORMUZ"})

    assert response.status_code == 200
    assert captured["max_hops"] == 2
