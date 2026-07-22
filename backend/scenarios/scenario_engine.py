"""Main scenario execution engine: loads the template matching scenario_type, applies manual_overrides, and
copies assumptions into the response (Phase 6, section 6.1; docs/SCENARIO_ASSUMPTIONS.md)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

import yaml

from ingestion.source_registry import get_freshness_state
from models.core_schema import Assumption, RiskLevel
from models.scenario_schema import AffectedRefinery, ScenarioRequest, ScenarioResult, ScenarioType
from reports.formatting import humanize as _humanize
from risk.exposure_model import get_exposed_refineries
from scenarios import impact_model
from services.digital_twin_service import DigitalTwinService

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# Scenario templates are analyst-authored YAML (section 6.1) and refer to
# chokepoints/entities by short labels that don't always match the Phase 2
# digital-twin's `entity_id` values verbatim (e.g. "BAB_EL_MANDEB" vs the
# seeded "CHK_BAB"). Kept as an explicit lookup - like Phase 4's
# `entity_resolution_agent.MANUAL_ALIASES` - rather than fuzzy-matched,
# since the template label set is small and fixed. Labels with no entry
# here (Phase 14 commodity entities not yet seeded, e.g. QATAR_EXPORT_TERMINAL)
# simply fail to resolve, and the engine falls back to capacity-weighted
# refinery exposure instead of crashing.
_ENTITY_LABEL_MAP: dict[str, list[str]] = {
    "HORMUZ": ["CHK_HORMUZ"],
    "BAB_EL_MANDEB": ["CHK_BAB"],
    "SUEZ": ["CHK_SUEZ"],
    "MALACCA": ["CHK_MALACCA"],
    # OPEC+ membership among the five seeded supplier countries.
    "OPEC_PLUS": ["SUP_IRQ", "SUP_KSA", "SUP_UAE", "SUP_RUS"],
    # No specific sanctioned supplier is named in the generic template;
    # Russia is India's largest crude supplier by import share, making it
    # the realistic stand-in for this scenario.
    "SANCTIONED_SUPPLIER": ["SUP_RUS"],
    "PARADIP": ["PRT_PAR"],
    "JNPT": ["PRT_MUM"],
}

_STALE_BASELINE_DAYS = 90


def _is_simulated_text(text: str) -> bool:
    """An assumption is `is_simulated` only if its own wording says so
    (e.g. "cargo ownership is simulated") rather than "estimated" (e.g.
    "import share data is estimated") - matching the distinction
    docs/SCENARIO_ASSUMPTIONS.md already draws between real-ish directional
    data and fully fabricated placeholders. Previously every template
    assumption was tagged `is_simulated=True` unconditionally, which made
    an "estimated" (real, if imprecise) figure indistinguishable from a
    "simulated" (fabricated) one in the API/UI."""
    return "simulated" in text.lower()


@dataclass
class ScenarioTemplate:
    scenario_type: ScenarioType
    commodity_type: str
    default_duration_days: int
    supply_reduction_percent_range: tuple[float, float]
    freight_cost_increase_percent_range: tuple[float, float]
    resolved_entity_ids: list[str]
    unresolved_labels: list[str]
    assumptions: list[str]


def _load_templates() -> dict[ScenarioType, ScenarioTemplate]:
    templates: dict[ScenarioType, ScenarioTemplate] = {}
    for path in sorted(_TEMPLATES_DIR.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text()) or {}
        scenario_type = ScenarioType(raw["scenario_type"])
        labels = list(raw.get("affected_chokepoints", [])) + list(raw.get("affected_entities", []))
        resolved_entity_ids = sorted(
            {entity_id for label in labels for entity_id in _ENTITY_LABEL_MAP.get(label, [])}
        )
        # Tracked per-label rather than folded into a single all-or-nothing
        # flag: a template like port_congestion.yaml (JNPT, SIKKA, PARADIP)
        # can have some labels resolve and others not, and that partial gap
        # should stay visible in the response even when enough of the
        # template resolved to still count as "uses graph relationships."
        unresolved_labels = sorted({label for label in labels if label not in _ENTITY_LABEL_MAP})
        templates[scenario_type] = ScenarioTemplate(
            scenario_type=scenario_type,
            commodity_type=raw["commodity_type"],
            default_duration_days=int(raw["default_duration_days"]),
            supply_reduction_percent_range=tuple(raw["supply_reduction_percent_range"]),
            freight_cost_increase_percent_range=tuple(raw["freight_cost_increase_percent_range"]),
            resolved_entity_ids=resolved_entity_ids,
            unresolved_labels=unresolved_labels,
            assumptions=list(raw.get("assumptions", [])),
        )
    return templates


def _load_default_digital_twin() -> DigitalTwinService:
    digital_twin = DigitalTwinService()
    digital_twin.load_seed_data()
    return digital_twin


class ScenarioEngine:
    """Runs Phase 6 scenario simulations end to end: template lookup,
    graph/digital-twin-derived refinery exposure, impact math, and
    assumption assembly."""

    def __init__(self, digital_twin: DigitalTwinService | None = None):
        self._templates = _load_templates()
        self._digital_twin = digital_twin or _load_default_digital_twin()

    def list_supported_scenarios(self) -> list[str]:
        return [scenario_type.value for scenario_type in self._templates]

    def get_resolved_entity_ids(self, scenario_type: ScenarioType) -> list[str]:
        """Digital-twin entity ids (chokepoints/suppliers/ports) a scenario
        template resolves to, so Phase 7's procurement agent can reuse the
        same resolution instead of re-deriving it from scratch."""
        return list(self._templates[scenario_type].resolved_entity_ids)

    def run(self, request: ScenarioRequest, *, scenario_id: str, created_at: datetime) -> ScenarioResult:
        template = self._templates[request.scenario_type]
        overrides_used: list[str] = []

        entity_ids = sorted(set(template.resolved_entity_ids) | set(request.affected_entities))
        affected_refineries, resolved_specific = self._resolve_affected_refineries(entity_ids, request.severity)
        route_transit_days = self._resolve_route_transit_days(entity_ids)

        supply_at_risk_percent = impact_model.compute_supply_at_risk_percent(
            template.supply_reduction_percent_range, request.severity, request.manual_overrides, overrides_used
        )
        freight_cost_impact_percent = impact_model.compute_freight_cost_impact_percent(
            template.freight_cost_increase_percent_range, request.severity, request.manual_overrides, overrides_used
        )
        estimated_delay_days = impact_model.compute_estimated_delay_days(
            default_duration_days=template.default_duration_days,
            duration_days=request.duration_days,
            severity=request.severity,
            affected_route_transit_days=route_transit_days,
            manual_overrides=request.manual_overrides,
            overrides_used=overrides_used,
        )
        stale_baseline = self._import_baseline_is_stale()
        confidence = impact_model.compute_confidence(
            manual_overrides_used=overrides_used,
            resolved_specific_entities=resolved_specific,
            duration_days=request.duration_days,
            default_duration_days=template.default_duration_days,
            stale_baseline=stale_baseline,
        )

        assumptions = [
            Assumption(description=text, is_simulated=_is_simulated_text(text)) for text in template.assumptions
        ]
        if overrides_used:
            # Disclosure that the user supplied a value directly - not
            # simulated/fabricated data, just naming which inputs are
            # user-provided rather than template/graph-derived.
            assumptions.append(
                Assumption(
                    description=(
                        f"Manual overrides applied for: {', '.join(_humanize(field) for field in overrides_used)}."
                    ),
                    is_simulated=False,
                )
            )
        if not resolved_specific:
            # The fallback heuristic itself uses real capacity data (see
            # `_resolve_affected_refineries`), just not a specific graph
            # chain - "estimated," not fabricated.
            assumptions.append(
                Assumption(
                    description=(
                        "Affected entities could not be matched to specific digital-twin nodes; "
                        "refinery exposure is estimated from overall capacity share rather than the "
                        "supply chain graph."
                    ),
                    is_simulated=False,
                )
            )
        elif template.unresolved_labels:
            # Some, but not all, of the template's labels resolved - still
            # counts as "uses graph relationships" overall, but the gap
            # itself must not disappear silently. Factual disclosure of a
            # data gap, not simulated data.
            assumptions.append(
                Assumption(
                    description=(
                        f"Template references entities with no digital-twin mapping yet: "
                        f"{', '.join(template.unresolved_labels)}; these contribute no graph-derived exposure."
                    ),
                    is_simulated=False,
                )
            )
        if stale_baseline:
            # Factual statement about data freshness, not simulated data.
            assumptions.append(
                Assumption(
                    description="India import baseline data is older than one quarter.",
                    is_simulated=False,
                )
            )

        return ScenarioResult(
            scenario_id=scenario_id,
            scenario_type=request.scenario_type,
            commodity_type=request.commodity_type,
            duration_days=request.duration_days,
            supply_at_risk_percent=min(100.0, supply_at_risk_percent),
            estimated_delay_days=estimated_delay_days,
            freight_cost_impact_percent=freight_cost_impact_percent,
            fuel_price_increase_percent=round(min(100.0, supply_at_risk_percent) * 0.4, 1),
            gdp_impact_percent=round(min(100.0, supply_at_risk_percent) * 0.015, 2),
            affected_refineries=affected_refineries,
            recommended_action_required=supply_at_risk_percent >= 15.0 or estimated_delay_days >= 7.0,
            confidence=confidence,
            assumptions=assumptions,
            created_at=created_at,
        )

    def _describe_entities(self, entity_ids: list[str]) -> str:
        """Human names for a list of digital-twin entity ids, comma-joined
        for prose (e.g. "Mumbai Port, Paradip Port" instead of raw
        "PRT_MUM, PRT_PAR"). Falls back to the raw id for anything the twin
        doesn't know about (e.g. an unresolved template label) rather than
        dropping it silently."""
        names = []
        for entity_id in entity_ids:
            entity = self._digital_twin.find_entity(entity_id)
            names.append(entity.name if entity is not None else entity_id)
        return ", ".join(names)

    def _resolve_affected_refineries(
        self, entity_ids: list[str], severity: RiskLevel
    ) -> tuple[list[AffectedRefinery], bool]:
        exposure_level = (
            RiskLevel.HIGH if severity in {RiskLevel.HIGH, RiskLevel.SEVERE, RiskLevel.CRITICAL} else RiskLevel.MEDIUM
        )
        weighted: dict[str, dict] = {}

        for entity_id in entity_ids:
            if entity_id.startswith("CHK_"):
                for row in get_exposed_refineries(self._digital_twin, entity_id):
                    weighted.setdefault(row["refinery_id"], row)
            elif entity_id.startswith("SUP_"):
                supplier = self._digital_twin.find_supplier(entity_id)
                route = self._digital_twin.routes.get(supplier.default_shipping_route_id) if supplier else None
                for chokepoint_id in (route.affected_chokepoint_ids if route else []):
                    for row in get_exposed_refineries(self._digital_twin, chokepoint_id):
                        weighted.setdefault(row["refinery_id"], row)
            elif entity_id.startswith("PRT_"):
                for refinery in self._digital_twin.get_refineries():
                    if entity_id in refinery.connected_import_port_ids:
                        weighted.setdefault(
                            refinery.id, {"refinery_id": refinery.id, "name": refinery.name}
                        )

        if weighted:
            reason = (
                "Digital-twin supply chain graph links this refinery to affected entities: "
                f"{self._describe_entities(entity_ids)}."
            )
            refineries = [
                AffectedRefinery(refinery_id=row["refinery_id"], exposure_level=exposure_level, reason=reason)
                for row in weighted.values()
            ]
            return refineries, True

        # Nothing resolved to a specific graph relationship (e.g. Phase 14
        # commodity entities not yet seeded, or a fully generic scenario
        # label) - fall back to the refineries with the largest overall
        # capacity share rather than an arbitrary hardcoded slice.
        ranked = sorted(
            self._digital_twin.get_refineries(), key=lambda ref: ref.capacity_bpd or 0, reverse=True
        )[:2]
        refineries = [
            AffectedRefinery(
                refinery_id=refinery.id,
                exposure_level=RiskLevel.MEDIUM,
                reason=f"No specific graph exposure resolved; {refinery.name} is included as a top-capacity refinery.",
            )
            for refinery in ranked
        ]
        return refineries, False

    def _resolve_route_transit_days(self, entity_ids: list[str]) -> list[float]:
        chokepoint_ids = {entity_id for entity_id in entity_ids if entity_id.startswith("CHK_")}
        if not chokepoint_ids:
            return []
        return [
            route.estimated_transit_days
            for route in self._digital_twin.get_routes()
            if route.estimated_transit_days is not None
            and chokepoint_ids.intersection(route.affected_chokepoint_ids)
        ]

    def _import_baseline_is_stale(self) -> bool:
        state = get_freshness_state("import_baseline")
        last_success = state.get("last_successful_fetch_at")
        if last_success is None:
            return True
        return (datetime.now(last_success.tzinfo) - last_success).days > _STALE_BASELINE_DAYS
