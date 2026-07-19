import pytest

from commodities.coal_adapter import CoalAdapter
from commodities.critical_minerals_adapter import CriticalMineralsAdapter
from commodities.crude_oil_adapter import CrudeOilAdapter
from commodities.fertilizer_adapter import FertilizerAdapter
from commodities.lng_adapter import LngAdapter

ALL_ADAPTERS = [CrudeOilAdapter(), LngAdapter(), CoalAdapter(), FertilizerAdapter(), CriticalMineralsAdapter()]


@pytest.mark.parametrize("adapter", ALL_ADAPTERS, ids=lambda a: a.commodity_type)
def test_adapter_returns_consistent_shapes(adapter):
    entities = adapter.get_supply_chain_entities()
    assert isinstance(entities, list)
    assert entities
    for entity in entities:
        assert "entity_type" in entity

    features = adapter.get_risk_features(signals=[{"x": 1}, {"x": 2}])
    assert isinstance(features, dict)
    assert all(isinstance(value, float) for value in features.values())

    templates = adapter.get_scenario_templates()
    assert isinstance(templates, list)
    assert templates
    assert all(isinstance(t, str) for t in templates)

    constraints = adapter.get_recommendation_constraints()
    assert isinstance(constraints, dict)
    assert constraints


def test_crude_oil_adapter_reuses_real_digital_twin_data():
    adapter = CrudeOilAdapter()
    entity_ids = {entity["entity_id"] for entity in adapter.get_supply_chain_entities()}
    assert "SUP_IRQ" in entity_ids
    assert "CHK_HORMUZ" in entity_ids


def test_non_crude_adapters_mark_entities_as_simulated():
    for adapter in [LngAdapter(), CoalAdapter(), FertilizerAdapter(), CriticalMineralsAdapter()]:
        entities = adapter.get_supply_chain_entities()
        assert all(entity.get("is_simulated") is True for entity in entities)


def test_commodity_types_are_all_distinct():
    commodity_types = {adapter.commodity_type for adapter in ALL_ADAPTERS}
    assert len(commodity_types) == len(ALL_ADAPTERS)
