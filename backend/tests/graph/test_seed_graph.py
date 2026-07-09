from graph import seed_graph


class _RecordingKGClient:
    """Fake KGClient that just records every Cypher write - every query in
    seed_graph.py is a MERGE, so "ran" is treated as "succeeded"."""

    def __init__(self):
        self.calls = []

    def run_query(self, cypher, parameters=None):
        self.calls.append((cypher, parameters or {}))
        return [{"matched": True}]


def test_load_seed_graph_creates_nodes_and_relationships():
    fake = _RecordingKGClient()

    counts = seed_graph.load_seed_graph(client=fake)

    assert counts["nodes"] > 0
    assert counts["relationships"] > 0

    merge_calls = [c for c in fake.calls if c[0].strip().startswith("MERGE (n:")]
    assert any(call[0].startswith("MERGE (n:SupplierCountry") for call in merge_calls)
    assert any(call[0].startswith("MERGE (n:ShippingRoute") for call in merge_calls)
    assert any(call[0].startswith("MERGE (n:Refinery") for call in merge_calls)


def test_entity_properties_flattens_coordinates_and_drops_nested_fields():
    from services.digital_twin_service import DigitalTwinService

    twin = DigitalTwinService()
    twin.load_seed_data()
    refinery = next(iter(twin.get_refineries()))

    props = seed_graph._entity_properties(refinery)

    assert "coordinates" not in props
    assert "metadata" not in props
    if refinery.coordinates:
        assert props["latitude"] == refinery.coordinates.latitude
        assert props["longitude"] == refinery.coordinates.longitude
