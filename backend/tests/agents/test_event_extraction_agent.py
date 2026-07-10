from datetime import datetime, timezone

from agents.event_extraction_agent import EventExtractionAgent, _extract_json_object, compute_confidence
from models.core_schema import SourceReliability
from models.data_source_schema import NormalizedSignal
from models.event_schema import RiskEvent
from services.digital_twin_service import DigitalTwinService


def _digital_twin() -> DigitalTwinService:
    service = DigitalTwinService()
    service.load_seed_data()
    return service


def _signal(
    signal_id,
    title,
    raw_text,
    country_hint=None,
    source_name="gdelt",
    reliability=SourceReliability.MEDIUM,
    is_simulated=False,
    url=None,
):
    return NormalizedSignal(
        signal_id=signal_id,
        source=source_name,
        source_name=source_name,
        source_reliability=reliability,
        reliability=reliability,
        detected_at=datetime.now(timezone.utc),
        title=title,
        raw_text=raw_text,
        country_hint=country_hint,
        is_simulated=is_simulated,
        url=url,
    )


class _FakeTextBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class _FakeMessage:
    def __init__(self, text):
        self.content = [_FakeTextBlock(text)]


class _FakeAnthropicClient:
    """Duck-typed stand-in for `anthropic.Anthropic` matching the
    `client.messages.create(...)` interface the agent calls."""

    def __init__(self, response_text):
        self._response_text = response_text
        self.messages = self
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _FakeMessage(self._response_text)


def _build_signal_fixture() -> list[NormalizedSignal]:
    """22 synthetic signals: 10 maritime-flavoured (chokepoint mentions),
    8 sanctions-flavoured (supplier mentions), and 4 with no resolvable
    location - proving both the ">=20 signals" and ">=80% resolution"
    Phase 4 validation checkpoints without depending on live network data.
    """
    chokepoints = ["Strait of Hormuz", "Bab el-Mandeb", "Suez Canal", "Malacca Strait"]
    suppliers = ["Iraq", "Russia", "Saudi Arabia", "UAE", "United States"]
    reliabilities = [
        SourceReliability.HIGH,
        SourceReliability.OFFICIAL,
        SourceReliability.MEDIUM,
        SourceReliability.LOW,
    ]

    signals: list[NormalizedSignal] = []
    counter = 0
    while len(signals) < 10:
        name = chokepoints[counter % len(chokepoints)]
        reliability = reliabilities[counter % len(reliabilities)]
        counter += 1
        signals.append(
            _signal(
                f"maritime-{counter}",
                f"Vessel incident reported near {name}",
                f"A tanker incident was reported while transiting {name}, disrupting normal traffic.",
                country_hint=name,
                reliability=reliability,
            )
        )

    counter = 0
    while len(signals) < 18:
        name = suppliers[counter % len(suppliers)]
        reliability = reliabilities[counter % len(reliabilities)]
        counter += 1
        signals.append(
            _signal(
                f"sanction-{counter}",
                f"New sanctions target {name} energy exports",
                f"Fresh sanctions were imposed affecting {name}'s crude export capacity.",
                country_hint=name,
                reliability=reliability,
            )
        )

    for index in range(4):
        signals.append(
            _signal(
                f"unresolvable-{index}",
                "Congestion reported across shipping lanes",
                "General congestion was reported without a specific corridor or port named.",
                country_hint=None,
                reliability=SourceReliability.MEDIUM,
            )
        )

    return signals


def test_extract_batch_converts_at_least_twenty_signals_with_high_resolution():
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=None)
    signals = _build_signal_fixture()
    assert len(signals) >= 20

    results = agent.extract_batch(signals)
    assert len(results) == len(signals)

    succeeded = [result for result in results if result.succeeded and result.event is not None]
    assert len(succeeded) >= 20

    resolved = [result for result in succeeded if result.event.affected_entities]
    resolution_rate = len(resolved) / len(succeeded)
    assert resolution_rate >= 0.8

    for result in succeeded:
        event = result.event
        assert isinstance(event, RiskEvent)
        assert event.event_type
        assert event.source_name
        assert event.detected_at is not None
        assert 1 <= event.severity <= 5
        assert 0.0 <= event.confidence <= 1.0


def test_extract_uses_official_alert_direct_for_official_source():
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=None)
    signal = _signal(
        "off-1",
        "Sanctions update",
        "New sanctions on Iraq shipping.",
        country_hint="Iraq",
        reliability=SourceReliability.OFFICIAL,
    )

    result = agent.extract(signal)

    assert result.succeeded
    assert result.extraction_method == "official_alert_direct"
    assert result.event.event_type == "SANCTION_UPDATE"
    assert "SUP_IRQ" in result.event.affected_entities


def test_extract_uses_rule_based_fallback_without_llm_client():
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=None)
    signal = _signal(
        "m-1",
        "Tension near Hormuz",
        "Rising tension reported near the Strait of Hormuz.",
        country_hint="Strait of Hormuz",
        reliability=SourceReliability.MEDIUM,
    )

    result = agent.extract(signal)

    assert result.succeeded
    assert result.extraction_method == "rule_based_fallback"
    assert "CHK_HORMUZ" in result.event.affected_entities


def test_extract_returns_unsucceeded_result_when_no_event_type_matches():
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=None)
    signal = _signal(
        "none-1",
        None,
        "Completely unrelated commentary with no notable keywords.",
        source_name="unknown_source",
        reliability=SourceReliability.MEDIUM,
    )

    result = agent.extract(signal)

    assert result.succeeded is False
    assert result.event is None
    assert result.error_message


def test_extract_uses_llm_when_available_for_non_official_source():
    fake_client = _FakeAnthropicClient(
        '{"event_type": "MARITIME_ATTACK", "commodity_type": "CRUDE_OIL", '
        '"title": "Tanker incident near Hormuz", "summary": "A tanker was attacked near Hormuz.", '
        '"severity": 4, "is_simulated": false}'
    )
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=fake_client)
    signal = _signal(
        "llm-1",
        "Tanker incident",
        "A tanker was reportedly attacked near the Strait of Hormuz.",
        country_hint="Strait of Hormuz",
        reliability=SourceReliability.MEDIUM,
    )

    result = agent.extract(signal)

    assert result.succeeded
    assert result.extraction_method == "llm"
    assert result.event.event_type == "MARITIME_ATTACK"
    assert result.event.severity == 4
    assert "CHK_HORMUZ" in result.event.affected_entities
    assert fake_client.calls


def test_extract_falls_back_when_llm_returns_invalid_json():
    fake_client = _FakeAnthropicClient("not valid json at all")
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=fake_client)
    signal = _signal(
        "llm-2",
        "Sanctions on Iraq",
        "New sanctions imposed on Iraq crude exports.",
        country_hint="Iraq",
        reliability=SourceReliability.MEDIUM,
    )

    result = agent.extract(signal)

    assert result.succeeded
    assert result.extraction_method == "rule_based_fallback"
    assert result.event.event_type == "SANCTION_UPDATE"


def test_extract_falls_back_when_llm_omits_event_type():
    fake_client = _FakeAnthropicClient('{"title": "no event type here"}')
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=fake_client)
    signal = _signal(
        "llm-3",
        "Sanctions on Russia",
        "New sanctions imposed on Russian crude exports.",
        country_hint="Russia",
        reliability=SourceReliability.MEDIUM,
    )

    result = agent.extract(signal)

    assert result.succeeded
    assert result.extraction_method == "rule_based_fallback"


def test_extract_evidence_urls_include_source_url():
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=None)
    signal = _signal(
        "url-1",
        "Sanctions on Iraq",
        "New sanctions imposed on Iraq crude exports.",
        country_hint="Iraq",
        reliability=SourceReliability.OFFICIAL,
        url="https://example.com/sanctions/iraq",
    )

    result = agent.extract(signal)

    assert result.event.evidence_urls == ["https://example.com/sanctions/iraq"]


def test_compute_confidence_rewards_official_source_and_resolved_entities():
    official_signal = _signal(
        "c1", "t", "Sanctions on Iraq", country_hint="Iraq", reliability=SourceReliability.OFFICIAL
    )
    low_signal = _signal("c2", "t", "no location details", country_hint=None, reliability=SourceReliability.LOW)

    high_confidence = compute_confidence(official_signal, ["SUP_IRQ"])
    low_confidence = compute_confidence(low_signal, [])

    assert high_confidence > low_confidence
    assert 0.0 <= high_confidence <= 1.0
    assert 0.0 <= low_confidence <= 1.0


def test_compute_confidence_caps_simulated_signals():
    simulated_signal = _signal(
        "c3",
        "t",
        "Official simulated data",
        country_hint="Iraq",
        reliability=SourceReliability.OFFICIAL,
        is_simulated=True,
    )
    assert compute_confidence(simulated_signal, ["SUP_IRQ"]) <= 0.6


def test_event_ids_are_sequential_per_year():
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=None)
    signal_a = _signal("seq-a", "Sanctions on Iraq", "New sanctions on Iraq.", reliability=SourceReliability.OFFICIAL)
    signal_b = _signal(
        "seq-b", "Sanctions on Russia", "New sanctions on Russia.", reliability=SourceReliability.OFFICIAL
    )

    event_a = agent.extract(signal_a).event
    event_b = agent.extract(signal_b).event

    assert event_a.event_id != event_b.event_id
    assert event_a.event_id.startswith(f"EVT-{datetime.now(timezone.utc).year}-")


def test_reset_event_sequence_restarts_ids_from_one():
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=None)
    signal = _signal("r-1", "Sanctions on Iraq", "New sanctions on Iraq.", reliability=SourceReliability.OFFICIAL)

    first_run_id = agent.extract(signal).event.event_id
    agent.reset_event_sequence()
    second_run_id = agent.extract(signal).event.event_id

    assert first_run_id == second_run_id


def test_extract_batch_boosts_confidence_for_corroborated_events():
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=None)
    signals = [
        _signal(
            "corrob-1",
            "Tension near Hormuz",
            "Rising tension reported near the Strait of Hormuz.",
            country_hint="Strait of Hormuz",
            source_name="gdelt",
            reliability=SourceReliability.MEDIUM,
        ),
        _signal(
            "corrob-2",
            "Hormuz tension escalates",
            "A second outlet also reports rising tension near the Strait of Hormuz.",
            country_hint="Strait of Hormuz",
            source_name="ais_stream",
            reliability=SourceReliability.MEDIUM,
        ),
    ]

    uncorroborated_result = agent.extract(
        _signal(
            "lone-1",
            "Tension near Hormuz",
            "Rising tension reported near the Strait of Hormuz.",
            country_hint="Strait of Hormuz",
            source_name="gdelt",
            reliability=SourceReliability.MEDIUM,
        )
    )
    baseline_confidence = uncorroborated_result.event.confidence

    results = agent.extract_batch(signals)

    for result in results:
        assert result.event.confidence > baseline_confidence


def test_extract_batch_does_not_boost_single_source_events():
    agent = EventExtractionAgent(digital_twin=_digital_twin(), llm_client=None)
    signal = _signal(
        "solo-1",
        "Sanctions on Iraq",
        "New sanctions on Iraq.",
        country_hint="Iraq",
        reliability=SourceReliability.OFFICIAL,
    )

    direct_confidence = agent.extract(signal).event.confidence
    agent.reset_event_sequence()
    [batched_result] = agent.extract_batch([signal])

    assert batched_result.event.confidence == direct_confidence


def test_extract_json_object_ignores_prose_around_the_json_block():
    text = (
        "Sure, here is the classification: "
        '{"event_type": "SANCTION_UPDATE", "severity": 3} '
        "Let me know if you need anything else {with a stray brace}."
    )

    payload = _extract_json_object(text)

    assert payload == {"event_type": "SANCTION_UPDATE", "severity": 3}


def test_extract_json_object_raises_when_nothing_parses():
    import pytest

    with pytest.raises(ValueError):
        _extract_json_object("no json here at all")
