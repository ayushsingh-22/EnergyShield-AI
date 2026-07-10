"""Links event text and coordinates to supplier, route, chokepoint, port,
refinery, and commodity graph nodes (Phase 4, section 4.3).

Resolution works against the in-memory `DigitalTwinService` seed data
rather than live Neo4j queries, so it degrades gracefully and stays
testable without a graph database. The resulting entity ids are exactly
the `entity_id`s `backend/graph/relationship_builder.py` expects when it
later creates AFFECTS edges.
"""

from __future__ import annotations

import re

from models.core_schema import Coordinates
from models.data_source_schema import NormalizedSignal
from services.digital_twin_service import DigitalTwinService

# Hand-curated aliases for shorthand that news/alert text commonly uses but
# that doesn't match a digital-twin entity's stored `name` verbatim (e.g.
# "Hormuz" instead of "Strait of Hormuz", "Red Sea" instead of "Bab el-Mandeb").
MANUAL_ALIASES: dict[str, str] = {
    "hormuz": "CHK_HORMUZ",
    "strait of hormuz": "CHK_HORMUZ",
    "bab el-mandeb": "CHK_BAB",
    "bab-el-mandeb": "CHK_BAB",
    "red sea": "CHK_BAB",
    "suez": "CHK_SUEZ",
    "suez canal": "CHK_SUEZ",
    "malacca": "CHK_MALACCA",
    "malacca strait": "CHK_MALACCA",
    "iraq": "SUP_IRQ",
    "russia": "SUP_RUS",
    "saudi arabia": "SUP_KSA",
    "uae": "SUP_UAE",
    "united arab emirates": "SUP_UAE",
    "united states": "SUP_USA",
}


class EntityResolutionAgent:
    """Resolves free-text location/entity hints in a `NormalizedSignal` to
    digital-twin entity ids."""

    def __init__(self, digital_twin: DigitalTwinService):
        self.digital_twin = digital_twin
        self._alias_index = self._build_alias_index()
        # Word-boundary patterns, compiled once, so a short alias like "uae"
        # can't match as a bare substring inside an unrelated word.
        self._alias_patterns = [
            (re.compile(r"\b" + re.escape(alias) + r"\b"), entity_id)
            for alias, entity_id in self._alias_index.items()
        ]

    def _build_alias_index(self) -> dict[str, str]:
        index: dict[str, str] = {}

        def add(alias: str | None, entity_id: str) -> None:
            if alias:
                index.setdefault(alias.strip().lower(), entity_id)

        for chokepoint in self.digital_twin.get_chokepoints():
            add(chokepoint.name, chokepoint.id)
            add(chokepoint.id, chokepoint.id)
        for supplier in self.digital_twin.get_suppliers():
            add(supplier.name, supplier.id)
            add(supplier.country, supplier.id)
            add(supplier.id, supplier.id)
        for refinery in self.digital_twin.get_refineries():
            add(refinery.name, refinery.id)
            add(refinery.location_name, refinery.id)
            add(refinery.id, refinery.id)
        for port in self.digital_twin.get_import_ports():
            add(port.name, port.id)
            add(port.id, port.id)
        for route in self.digital_twin.get_routes():
            add(route.name, route.id)
            add(route.id, route.id)

        # Manual aliases never override a real entity name/id already indexed.
        for alias, entity_id in MANUAL_ALIASES.items():
            index.setdefault(alias, entity_id)
        return index

    def resolve(self, signal: NormalizedSignal) -> list[str]:
        """Best-effort substring match of the signal's location hint,
        title, and raw text against the alias index. An empty result means
        "location unresolved", not an error - callers must not crash on it
        (Coding-Agent Instruction: never drop a signal because text is messy).
        """
        haystack = " ".join(
            part for part in (signal.country_hint, signal.title, signal.raw_text) if part
        ).lower()
        if not haystack:
            return []

        matched = {entity_id for pattern, entity_id in self._alias_patterns if pattern.search(haystack)}
        return sorted(matched)

    def expand_via_routes(self, entity_ids: list[str]) -> list[str]:
        """Adds shipping routes that transit a matched chokepoint, so a
        single chokepoint mention also flags the routes it threatens
        without requiring a live graph traversal."""
        expanded = set(entity_ids)
        chokepoint_ids = {entity_id for entity_id in entity_ids if entity_id.startswith("CHK_")}
        if chokepoint_ids:
            for route in self.digital_twin.get_routes():
                if chokepoint_ids.intersection(route.affected_chokepoint_ids):
                    expanded.add(route.id)
        return sorted(expanded)

    def resolve_coordinates(self, entity_ids: list[str]) -> Coordinates | None:
        """Best-effort representative point for the event: a matched
        entity's own coordinates, or the centroid of a matched
        chokepoint's polygon."""
        for entity_id in entity_ids:
            chokepoint = self.digital_twin.chokepoints.get(entity_id)
            if chokepoint and chokepoint.geometry:
                ring = (chokepoint.geometry.get("coordinates") or [[]])[0]
                if ring:
                    longitudes = [point[0] for point in ring]
                    latitudes = [point[1] for point in ring]
                    return Coordinates(
                        latitude=sum(latitudes) / len(latitudes),
                        longitude=sum(longitudes) / len(longitudes),
                    )
            entity = self.digital_twin.find_entity(entity_id)
            if entity is not None and getattr(entity, "coordinates", None):
                return entity.coordinates
        return None
