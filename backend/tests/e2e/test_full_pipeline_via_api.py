"""End-to-end tests against the real `main.app` (every router wired together,
matching how the deployed app actually serves requests) rather than the
single-router test apps the rest of `backend/tests/api/` builds.

Exercises the Phase 12 "Recommended Demo Flow": run a scenario -> fetch its
recommendation -> generate a report -> confirm the audit trail can
reconstruct the whole chain - plus the Phase 13 learning and Phase 14
multi-commodity surfaces the same app serves.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

import main

# Not using `with TestClient(...)` deliberately: that would trigger
# `main.py`'s startup handlers (init_db against a real Postgres, and
# starting the Phase 10 background scheduler thread), which this test
# doesn't need and shouldn't leave running after the test session ends.
client = TestClient(main.app)

SCENARIO_REQUEST = {
    "scenario_type": "HORMUZ_PARTIAL_CLOSURE",
    "commodity_type": "CRUDE_OIL",
    "duration_days": 15,
    "severity": "HIGH",
    "affected_entities": ["CHK_HORMUZ"],
    "manual_overrides": {},
}


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_full_signal_to_recommendation_to_report_chain():
    scenario_response = client.post("/api/v1/scenarios/run", json=SCENARIO_REQUEST)
    assert scenario_response.status_code == 200
    scenario = scenario_response.json()
    assert scenario["assumptions"]
    assert scenario["affected_refineries"]

    recommendation_response = client.get(f"/api/v1/recommendations/{scenario['scenario_id']}")
    assert recommendation_response.status_code == 200
    recommendation = recommendation_response.json()
    assert recommendation["audit_id"]

    report_response = client.post("/api/v1/reports/generate", json={"scenario_id": scenario["scenario_id"]})
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["report_markdown"]

    # Auditability (Phase 11 validation): the audit trail can reconstruct
    # the path from scenario to recommendation without any other input.
    scenario_audit = client.get(f"/api/v1/audit/{scenario['scenario_id']}").json()
    assert any(entry["action"] == "SCENARIO_RUN" for entry in scenario_audit)

    recommendation_audit = client.get(f"/api/v1/audit/{recommendation['recommendation_id']}").json()
    assert any(entry["action"] == "RECOMMENDATION_GENERATED" for entry in recommendation_audit)


def test_learning_endpoints_are_wired():
    cases = client.get("/api/v1/learning/cases").json()
    assert len(cases) >= 3

    backtest = client.post("/api/v1/learning/backtest", json={}).json()
    assert "precision" in backtest
    assert client.get(f"/api/v1/learning/backtest/{backtest['run_id']}").status_code == 200

    feedback = client.post(
        "/api/v1/learning/feedback",
        json={"recommendation_id": "REC-TEST", "useful": True, "action_taken": "ACCEPTED"},
    )
    assert feedback.status_code == 200


def test_multi_commodity_endpoints_are_wired_for_every_commodity():
    commodities = client.get("/api/v1/commodities").json()
    assert len(commodities) == 5

    for commodity in commodities:
        commodity_type = commodity["commodity_type"]
        entities = client.get(f"/api/v1/commodities/{commodity_type}/entities")
        assert entities.status_code == 200
        assert entities.json()["entity_count"] > 0

        scenarios = client.get(f"/api/v1/commodities/{commodity_type}/scenarios")
        assert scenarios.status_code == 200
        assert scenarios.json()
