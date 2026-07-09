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
