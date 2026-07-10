"""Event taxonomy: keyword-to-event-type rules, severity heuristics, and
scenario trigger mapping (Phase 4, sections 4.1 and 4.2).

Purely deterministic and dependency-free so it can back both the
`official_alert_direct` path and the `rule_based_fallback` path used when
the LLM is unavailable or its output fails validation (Coding-Agent
Instruction: any LLM-generated output must have deterministic fallback
logic).
"""

from __future__ import annotations

from models.core_schema import RiskEventType

# Deterministic per-source default event type, used when no keyword in the
# signal text overrides it. Keeps classification stable for terse official
# alerts that don't repeat obvious keywords (e.g. a sanctions snapshot
# titled just "OFAC Update").
SOURCE_DEFAULT_EVENT_TYPE: dict[str, RiskEventType] = {
    "sanctions": RiskEventType.SANCTION_UPDATE,
    "commodity_prices": RiskEventType.PRICE_SPIKE,
    "ais_stream": RiskEventType.AIS_REROUTING,
    "portwatch": RiskEventType.CHOKEPOINT_CONGESTION,
    "maritime_alerts": RiskEventType.MARITIME_ATTACK,
}

# Ordered keyword -> event type rules. Checked in order, first match wins,
# so more specific phrases are listed before generic ones (e.g. "sanction"
# before the generic political-instability bucket).
KEYWORD_EVENT_TYPES: list[tuple[list[str], RiskEventType]] = [
    (["sanction"], RiskEventType.SANCTION_UPDATE),
    (["opec", "supply cut", "production cut"], RiskEventType.OPEC_SUPPLY_CUT),
    (["export ban", "export restriction", "export curb"], RiskEventType.EXPORT_RESTRICTION),
    (["price spike", "price surge", "spiked", "price jump"], RiskEventType.PRICE_SPIKE),
    (["reroute", "rerouting", "diverted", "altered course"], RiskEventType.AIS_REROUTING),
    (["port closure", "port closed", "port shut"], RiskEventType.PORT_CLOSURE),
    (["congestion", "backlog", "wait time", "queue"], RiskEventType.CHOKEPOINT_CONGESTION),
    (["refinery fire", "refinery outage", "refinery shutdown"], RiskEventType.REFINERY_SUPPLY_RISK),
    (["storm", "cyclone", "hurricane", "weather"], RiskEventType.WEATHER_DISRUPTION),
    (["attack", "incident", "strike", "explosion", "hijack", "seized", "seizure"], RiskEventType.MARITIME_ATTACK),
    (["coup", "unrest", "protest", "instability", "tension"], RiskEventType.POLITICAL_INSTABILITY),
]

BASE_SEVERITY_BY_EVENT_TYPE: dict[RiskEventType, int] = {
    RiskEventType.MARITIME_ATTACK: 4,
    RiskEventType.PORT_CLOSURE: 4,
    RiskEventType.SANCTION_UPDATE: 3,
    RiskEventType.OPEC_SUPPLY_CUT: 4,
    RiskEventType.PRICE_SPIKE: 3,
    RiskEventType.AIS_REROUTING: 2,
    RiskEventType.CHOKEPOINT_CONGESTION: 2,
    RiskEventType.REFINERY_SUPPLY_RISK: 3,
    RiskEventType.EXPORT_RESTRICTION: 3,
    RiskEventType.WEATHER_DISRUPTION: 2,
    RiskEventType.POLITICAL_INSTABILITY: 2,
}

SEVERITY_UP_KEYWORDS = ["major", "severe", "critical", "total closure", "full closure", "explosion"]
SEVERITY_DOWN_KEYWORDS = ["minor", "partial", "temporary", "brief"]

# MVP scenario templates (Phase 6) a chokepoint disruption can trigger.
CHOKEPOINT_SCENARIO_TRIGGERS: dict[str, list[str]] = {
    "CHK_HORMUZ": ["HORMUZ_PARTIAL_CLOSURE"],
    "CHK_BAB": ["RED_SEA_SHIPPING_DISRUPTION"],
    "CHK_SUEZ": ["RED_SEA_SHIPPING_DISRUPTION"],
}

EVENT_TYPE_SCENARIO_TRIGGERS: dict[RiskEventType, list[str]] = {
    RiskEventType.SANCTION_UPDATE: ["SANCTIONS_SHOCK"],
    RiskEventType.OPEC_SUPPLY_CUT: ["OPEC_SUPPLY_CUT"],
    RiskEventType.PORT_CLOSURE: ["PORT_CONGESTION"],
    RiskEventType.CHOKEPOINT_CONGESTION: ["PORT_CONGESTION"],
}


def classify_event_type(signal) -> RiskEventType | None:
    """Rule-based event-type classification.

    `signal` is a `models.data_source_schema.NormalizedSignal`. Returns
    `None` when neither the text nor the source name yields a confident
    match - callers must treat that as "not an event" rather than guessing.
    """
    text = " ".join(part for part in (signal.title, signal.raw_text) if part).lower()
    for keywords, event_type in KEYWORD_EVENT_TYPES:
        if any(keyword in text for keyword in keywords):
            return event_type
    return SOURCE_DEFAULT_EVENT_TYPE.get(signal.source_name)


def estimate_severity(event_type: RiskEventType, text: str) -> int:
    """Severity 1-5 (plan section 4.1): a per-event-type base, nudged up or
    down by intensity language in the source text."""
    severity = BASE_SEVERITY_BY_EVENT_TYPE.get(event_type, 2)
    lowered = text.lower()
    if any(keyword in lowered for keyword in SEVERITY_UP_KEYWORDS):
        severity += 1
    if any(keyword in lowered for keyword in SEVERITY_DOWN_KEYWORDS):
        severity -= 1
    return max(1, min(5, severity))


def get_scenario_triggers(event_type: RiskEventType | str | None, affected_entity_ids: list[str]) -> list[str]:
    """Candidate Phase 6 scenario templates this event could trigger."""
    triggers: set[str] = set(EVENT_TYPE_SCENARIO_TRIGGERS.get(event_type, []))
    for entity_id in affected_entity_ids:
        triggers.update(CHOKEPOINT_SCENARIO_TRIGGERS.get(entity_id, []))
    return sorted(triggers)
