from graph import graph_queries


class _FakeKGClient:
    """Duck-typed stand-in for graph.kg_client.KGClient that records the
    Cypher/parameters it was called with and returns canned rows."""

    def __init__(self, rows):
        self.rows = rows
        self.calls = []

    def run_query(self, cypher, parameters=None):
        self.calls.append((cypher, parameters or {}))
        return self.rows


def test_get_refineries_exposed_to_chokepoint(monkeypatch):
    fake = _FakeKGClient([{"entity_id": "REF_JAM", "name": "Reliance Jamnagar", "risk_level": "HIGH"}])
    monkeypatch.setattr(graph_queries, "get_kg_client", lambda: fake)

    result = graph_queries.get_refineries_exposed_to_chokepoint("CHK_HORMUZ")

    assert result == [{"entity_id": "REF_JAM", "name": "Reliance Jamnagar", "risk_level": "HIGH"}]
    assert fake.calls[0][1] == {"chokepoint_id": "CHK_HORMUZ"}


def test_get_alternative_suppliers(monkeypatch):
    fake = _FakeKGClient([{"entity_id": "SUP_KSA", "name": "Saudi Arabia", "region": "Middle East"}])
    monkeypatch.setattr(graph_queries, "get_kg_client", lambda: fake)

    result = graph_queries.get_alternative_suppliers("CRUDE_OIL", "SUP_IRQ")

    assert result[0]["entity_id"] == "SUP_KSA"
    assert fake.calls[0][1] == {"commodity": "CRUDE_OIL", "blocked_supplier_id": "SUP_IRQ"}


def test_get_routes_for_supplier(monkeypatch):
    fake = _FakeKGClient([{"entity_id": "RT_BAS_JAM", "name": "Basra to Jamnagar"}])
    monkeypatch.setattr(graph_queries, "get_kg_client", lambda: fake)

    result = graph_queries.get_routes_for_supplier("SUP_IRQ")

    assert result[0]["entity_id"] == "RT_BAS_JAM"
    assert fake.calls[0][1] == {"supplier_id": "SUP_IRQ"}


def test_get_scenarios_triggered_by_event(monkeypatch):
    fake = _FakeKGClient([{"entity_id": "SCN-2026-0001", "scenario_type": "HORMUZ_PARTIAL_CLOSURE"}])
    monkeypatch.setattr(graph_queries, "get_kg_client", lambda: fake)

    result = graph_queries.get_scenarios_triggered_by_event("EVT-2026-0001")

    assert result[0]["entity_id"] == "SCN-2026-0001"
    assert fake.calls[0][1] == {"event_id": "EVT-2026-0001"}


def test_get_spr_sites_for_refinery(monkeypatch):
    fake = _FakeKGClient([{"entity_id": "SPR_MAN", "name": "Mangalore SPR", "drawdown_priority": 1}])
    monkeypatch.setattr(graph_queries, "get_kg_client", lambda: fake)

    result = graph_queries.get_spr_sites_for_refinery("REF_MAN")

    assert result[0]["entity_id"] == "SPR_MAN"
    assert fake.calls[0][1] == {"refinery_id": "REF_MAN"}


def test_get_entity_neighborhood_not_found(monkeypatch):
    fake = _FakeKGClient([])
    monkeypatch.setattr(graph_queries, "get_kg_client", lambda: fake)

    result = graph_queries.get_entity_neighborhood("UNKNOWN")

    assert result["nodes"] == []
    assert result["edges"] == []


def test_get_entity_neighborhood_merges_outgoing_and_incoming(monkeypatch):
    call_results = [
        [{"labels": ["Chokepoint"], "properties": {"name": "Strait of Hormuz"}}],
        [{"relationship_type": "TRANSITS", "other_id": "RT_BAS_JAM", "properties": {}}],
        [{"relationship_type": "AFFECTS", "other_id": "EVT-1", "properties": {"confidence": 0.8}}],
    ]

    class _SequencedClient:
        def run_query(self, cypher, parameters=None):
            return call_results.pop(0)

    monkeypatch.setattr(graph_queries, "get_kg_client", lambda: _SequencedClient())

    result = graph_queries.get_entity_neighborhood("CHK_HORMUZ")

    assert result["nodes"] == [{"entity_id": "CHK_HORMUZ", "label": "Chokepoint", "properties": {"name": "Strait of Hormuz"}}]
    assert len(result["edges"]) == 2
    outgoing = next(e for e in result["edges"] if e["target_id"] == "RT_BAS_JAM")
    assert outgoing["source_id"] == "CHK_HORMUZ"
    incoming = next(e for e in result["edges"] if e["source_id"] == "EVT-1")
    assert incoming["target_id"] == "CHK_HORMUZ"
    assert incoming["confidence"] == 0.8


def test_get_impact_subgraph_empty(monkeypatch):
    fake = _FakeKGClient([])
    monkeypatch.setattr(graph_queries, "get_kg_client", lambda: fake)

    result = graph_queries.get_impact_subgraph("CHK_HORMUZ", max_hops=3)

    assert result["nodes"] == []
    assert result["edges"] == []


def test_get_impact_subgraph_clamps_hops_and_builds_nodes(monkeypatch):
    fake = _FakeKGClient(
        [
            {
                "source_id": "CHK_HORMUZ",
                "source_labels": ["Chokepoint"],
                "source_properties": {},
                "relationship_type": "TRANSITS",
                "rel_properties": {},
                "target_id": "RT_BAS_JAM",
                "target_labels": ["ShippingRoute"],
                "target_properties": {},
            }
        ]
    )
    monkeypatch.setattr(graph_queries, "get_kg_client", lambda: fake)

    result = graph_queries.get_impact_subgraph("CHK_HORMUZ", max_hops=99)

    # max_hops is clamped to 5 before being interpolated into the Cypher text.
    assert "*1..5" in fake.calls[0][0]
    assert {n["entity_id"] for n in result["nodes"]} == {"CHK_HORMUZ", "RT_BAS_JAM"}
    assert result["edges"][0]["relationship_type"] == "TRANSITS"
