from datetime import datetime, timezone

from agents.entity_resolution_agent import EntityResolutionAgent
from models.core_schema import SourceReliability
from models.data_source_schema import NormalizedSignal
from services.digital_twin_service import DigitalTwinService


def _digital_twin() -> DigitalTwinService:
    service = DigitalTwinService()
    service.load_seed_data()
    return service


def _signal(country_hint=None, title=None, raw_text=""):
    return NormalizedSignal(
        signal_id="sig-1",
        source="gdelt",
        source_name="gdelt",
        source_reliability=SourceReliability.MEDIUM,
        reliability=SourceReliability.MEDIUM,
        detected_at=datetime.now(timezone.utc),
        country_hint=country_hint,
        title=title,
        raw_text=raw_text,
    )


def test_resolve_matches_chokepoint_alias():
    agent = EntityResolutionAgent(_digital_twin())
    signal = _signal(country_hint="Strait of Hormuz")
    assert agent.resolve(signal) == ["CHK_HORMUZ"]


def test_resolve_matches_supplier_by_country_name():
    agent = EntityResolutionAgent(_digital_twin())
    signal = _signal(raw_text="New restrictions target Iraq crude exports.")
    assert "SUP_IRQ" in agent.resolve(signal)


def test_resolve_returns_empty_for_unresolvable_text():
    agent = EntityResolutionAgent(_digital_twin())
    signal = _signal(country_hint="Nowhere Notable")
    assert agent.resolve(signal) == []


def test_expand_via_routes_adds_transiting_routes():
    agent = EntityResolutionAgent(_digital_twin())
    expanded = agent.expand_via_routes(["CHK_HORMUZ"])
    assert "RT_BAS_JAM" in expanded
    assert "RT_RAS_MUN" in expanded


def test_expand_via_routes_noop_when_no_chokepoints():
    agent = EntityResolutionAgent(_digital_twin())
    assert agent.expand_via_routes(["SUP_IRQ"]) == ["SUP_IRQ"]


def test_resolve_coordinates_from_chokepoint_centroid():
    agent = EntityResolutionAgent(_digital_twin())
    coordinates = agent.resolve_coordinates(["CHK_HORMUZ"])
    assert coordinates is not None
    assert 26.0 <= coordinates.latitude <= 27.0
    assert 55.0 <= coordinates.longitude <= 56.5


def test_resolve_coordinates_returns_none_when_unresolvable():
    agent = EntityResolutionAgent(_digital_twin())
    assert agent.resolve_coordinates([]) is None


def test_resolve_does_not_false_positive_on_short_alias_substring():
    """"uae" is a real alias (SUP_UAE) but must not match when it's merely
    a substring inside a longer unrelated token with no word boundary
    around it - a plain `"uae" in text` check would wrongly match here."""
    agent = EntityResolutionAgent(_digital_twin())
    signal = _signal(raw_text="A company called SubsidiaryUAEHoldings was mentioned in passing.")
    assert agent.resolve(signal) == []


def test_resolve_still_matches_uae_as_a_whole_word():
    agent = EntityResolutionAgent(_digital_twin())
    signal = _signal(raw_text="New export restrictions were announced by the UAE today.")
    assert "SUP_UAE" in agent.resolve(signal)
