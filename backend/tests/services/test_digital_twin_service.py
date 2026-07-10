from pathlib import Path
from services.digital_twin_service import DigitalTwinService

def test_service_initialization():
    service = DigitalTwinService()
    assert service.suppliers == {}

def test_load_seed_data():
    service = DigitalTwinService()
    service.load_seed_data()
    # Check if some data loaded
    assert len(service.suppliers) > 0
    assert len(service.export_ports) > 0
    assert len(service.routes) > 0

def test_exposure_summary():
    service = DigitalTwinService()
    service.load_seed_data()
    summary = service.get_exposure_summary()
    assert summary["total_supplier_exposure_percent"] > 0
    assert summary["total_refineries"] > 0

def test_find_entity():
    service = DigitalTwinService()
    service.load_seed_data()
    # Assume SUP_IRQ exists in our seed
    entity = service.find_entity("SUP_IRQ")
    assert entity is not None
    assert entity.id == "SUP_IRQ"
    assert entity.name == "Iraq"


def test_every_supplier_default_route_exists(caplog):
    """Phase 2 validation checklist: 'Every supplier has at least one
    route.' Regression test for the SUP_UAE/SUP_USA routes that used to
    reference RT_FUJ_MAN/RT_HOU_PAR before those routes existed."""
    service = DigitalTwinService()
    service.load_seed_data()

    for supplier in service.get_suppliers():
        assert supplier.default_shipping_route_id in service.routes, (
            f"{supplier.id} references a route not present in the loaded seed data"
        )

    with caplog.at_level("WARNING"):
        service.get_exposure_summary()
    assert "not in the loaded route seed data" not in caplog.text


def test_exposure_summary_includes_data_source_breakdown():
    service = DigitalTwinService()
    service.load_seed_data()

    summary = service.get_exposure_summary()

    assert "exposure_by_data_source" in summary
    total = sum(summary["exposure_by_data_source"].values())
    assert round(total, 3) == round(summary["total_supplier_exposure_percent"], 3)
