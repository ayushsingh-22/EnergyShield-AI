from graph import graph_queries
from optimization import procurement_optimizer
from services.digital_twin_service import DigitalTwinService


class _FakeKGClient:
    """Duck-typed stand-in for graph.kg_client.KGClient, matching the
    pattern in tests/graph/test_graph_queries.py - real network calls to
    an unreachable Neo4j can each take tens of seconds to time out, so
    every test here monkeypatches this in instead."""

    def __init__(self, rows):
        self.rows = rows

    def run_query(self, cypher, parameters=None):
        return self.rows


def _digital_twin() -> DigitalTwinService:
    twin = DigitalTwinService()
    twin.load_seed_data()
    return twin


def _no_graph_data(monkeypatch):
    """Simulates no live graph (or a graph with no matching rows), so
    `find_candidate_suppliers` exercises its digital-twin fallback path."""
    monkeypatch.setattr(graph_queries, "get_kg_client", lambda: _FakeKGClient([]))


def test_find_blocked_suppliers_via_chokepoint():
    twin = _digital_twin()
    # SUP_IRQ (RT_BAS_JAM) and SUP_KSA (RT_RAS_MUN) both transit CHK_HORMUZ.
    blocked = procurement_optimizer.find_blocked_suppliers(twin, ["CHK_HORMUZ"])
    assert set(blocked) == {"SUP_IRQ", "SUP_KSA"}


def test_find_blocked_suppliers_direct_ids_passthrough():
    twin = _digital_twin()
    blocked = procurement_optimizer.find_blocked_suppliers(twin, ["SUP_RUS"])
    assert blocked == ["SUP_RUS"]


def test_find_candidate_suppliers_excludes_blocked_and_high_risk(monkeypatch):
    _no_graph_data(monkeypatch)
    twin = _digital_twin()
    candidates = procurement_optimizer.find_candidate_suppliers(
        twin, "CRUDE_OIL", blocked_supplier_ids=["SUP_IRQ", "SUP_KSA"], high_risk_affected_entities={"SUP_UAE"}
    )
    candidate_ids = {c.id for c in candidates}
    assert "SUP_IRQ" not in candidate_ids
    assert "SUP_KSA" not in candidate_ids
    assert "SUP_UAE" not in candidate_ids
    assert candidate_ids  # SUP_RUS/SUP_USA should remain


def test_find_candidate_suppliers_prefers_graph_result_when_available(monkeypatch):
    monkeypatch.setattr(
        graph_queries, "get_kg_client", lambda: _FakeKGClient([{"entity_id": "SUP_RUS"}])
    )
    twin = _digital_twin()
    candidates = procurement_optimizer.find_candidate_suppliers(twin, "CRUDE_OIL", blocked_supplier_ids=["SUP_IRQ"])
    assert [c.id for c in candidates] == ["SUP_RUS"]


def test_rank_procurement_options_orders_best_first_and_caps_length(monkeypatch):
    _no_graph_data(monkeypatch)
    twin = _digital_twin()
    candidates = procurement_optimizer.find_candidate_suppliers(twin, "CRUDE_OIL", blocked_supplier_ids=[])
    options = procurement_optimizer.rank_procurement_options(
        twin, candidates, freight_cost_impact_percent=15.0, action_required=True, max_options=3
    )
    assert 1 <= len(options) <= 3
    assert [option.rank for option in options] == list(range(1, len(options) + 1))
    scores = [option.feasibility_score for option in options]
    assert scores == sorted(scores, reverse=True)
    assert options[0].action_priority == "IMMEDIATE"
