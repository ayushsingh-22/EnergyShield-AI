from datetime import datetime, timezone

from models.core_schema import CommodityType, RiskLevel
from models.scenario_schema import ScenarioRequest, ScenarioType
from scenarios.scenario_engine import ScenarioEngine
from services.digital_twin_service import DigitalTwinService
from services.scenario_service import ScenarioService


def _digital_twin() -> DigitalTwinService:
    service = DigitalTwinService()
    service.load_seed_data()
    return service


def _request(**overrides) -> ScenarioRequest:
    defaults = dict(
        scenario_type=ScenarioType.HORMUZ_PARTIAL_CLOSURE,
        commodity_type=CommodityType.CRUDE_OIL,
        duration_days=15,
        severity=RiskLevel.HIGH,
        affected_entities=[],
        manual_overrides={},
    )
    defaults.update(overrides)
    return ScenarioRequest(**defaults)


def test_run_scenario_is_retrievable_from_in_memory_cache():
    service = ScenarioService(engine=ScenarioEngine(_digital_twin()))

    result = service.run_scenario(_request())
    fetched = service.get_scenario(result.scenario_id)

    assert fetched == result


def test_get_scenario_unknown_id_with_no_db_row_returns_none():
    service = ScenarioService(engine=ScenarioEngine(_digital_twin()))
    assert service.get_scenario("SCN-NEVER-RUN") is None


def test_get_scenario_falls_back_to_repository_when_not_in_memory(monkeypatch):
    """Regression test: `repository.get_scenario_run` used to be dead code
    - a scenario run written to Postgres could never actually be read back
    after a process restart, which this simulates by clearing the
    in-memory cache and stubbing the repository read."""
    service = ScenarioService(engine=ScenarioEngine(_digital_twin()))
    result = service.run_scenario(_request())

    service._results.clear()  # simulate a process restart wiping in-memory state
    monkeypatch.setattr(
        "services.scenario_service.repository.get_scenario_run",
        lambda scenario_id: [{"payload": result.model_dump_json()}],
    )

    fetched = service.get_scenario(result.scenario_id)

    assert fetched is not None
    assert fetched.scenario_id == result.scenario_id
    assert fetched.supply_at_risk_percent == result.supply_at_risk_percent


def test_get_scenario_handles_corrupt_repository_row_gracefully(monkeypatch):
    service = ScenarioService(engine=ScenarioEngine(_digital_twin()))
    monkeypatch.setattr(
        "services.scenario_service.repository.get_scenario_run",
        lambda scenario_id: [{"payload": "not valid json"}],
    )

    assert service.get_scenario("SCN-CORRUPT") is None
