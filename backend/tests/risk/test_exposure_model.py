from risk import exposure_model
from services.digital_twin_service import DigitalTwinService


def _digital_twin() -> DigitalTwinService:
    service = DigitalTwinService()
    service.load_seed_data()
    return service


def test_compute_chokepoint_exposure_score_matches_summary():
    twin = _digital_twin()
    summary = twin.get_exposure_summary()

    score = exposure_model.compute_chokepoint_exposure_score(twin, "CHK_HORMUZ")

    assert score == round(summary["chokepoint_exposure_percent"]["CHK_HORMUZ"], 2)
    assert score > 0


def test_compute_chokepoint_exposure_score_unknown_chokepoint_is_zero():
    twin = _digital_twin()
    assert exposure_model.compute_chokepoint_exposure_score(twin, "CHK_UNKNOWN") == 0.0


def test_compute_route_exposure_score_positive_for_seeded_route():
    twin = _digital_twin()
    assert exposure_model.compute_route_exposure_score(twin, "RT_BAS_JAM") > 0


def test_compute_supplier_exposure_score_matches_import_share():
    twin = _digital_twin()
    supplier = twin.find_supplier("SUP_IRQ")

    assert exposure_model.compute_supplier_exposure_score(twin, "SUP_IRQ") == round(supplier.import_share_percent, 2)


def test_compute_supplier_exposure_score_unknown_supplier_is_zero():
    twin = _digital_twin()
    assert exposure_model.compute_supplier_exposure_score(twin, "SUP_UNKNOWN") == 0.0


def test_get_exposed_refineries_for_hormuz_includes_jamnagar():
    twin = _digital_twin()
    exposed = exposure_model.get_exposed_refineries(twin, "CHK_HORMUZ")

    assert exposed
    assert any(item["refinery_id"] == "REF_JAM" for item in exposed)
    for item in exposed:
        assert 0 <= item["capacity_weight_percent"] <= 100


def test_get_exposed_refineries_for_chokepoint_with_no_routes_is_empty():
    twin = _digital_twin()
    assert exposure_model.get_exposed_refineries(twin, "CHK_MALACCA") == []
