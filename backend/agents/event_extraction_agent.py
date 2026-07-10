"""Main extraction pipeline converting normalized signals into structured
risk events (Phase 4, sections 4.2-4.4).

Every signal goes through one of three paths, in order of precedence:

1. `official_alert_direct` - deterministic rules for OFFICIAL/HIGH
   reliability sources (official alerts, sanctions snapshots).
2. `llm` - an LLM call for messier text (e.g. news), only attempted when
   an Anthropic client is configured.
3. `rule_based_fallback` - the same deterministic rules used for path 1,
   used whenever the LLM is unavailable or its output fails validation.

Every path produces a valid `RiskEvent` or none at all - the pipeline never
raises on a single bad signal (Coding-Agent Instruction: any LLM-generated
output must have deterministic fallback logic).
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path

from agents.entity_resolution_agent import EntityResolutionAgent
from ml import event_classifier
from models.core_schema import CommodityType, SourceReliability
from models.data_source_schema import NormalizedSignal
from models.event_schema import ExtractionResult, RiskEvent
from services.digital_twin_service import DigitalTwinService

logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "risk_event_extraction.md"

_RELIABILITY_CONFIDENCE_BASE: dict[str, float] = {
    SourceReliability.OFFICIAL: 0.95,
    SourceReliability.HIGH: 0.85,
    SourceReliability.MEDIUM: 0.65,
    SourceReliability.LOW: 0.45,
    SourceReliability.SIMULATED: 0.5,
}

# Official alerts and sanctions snapshots are extracted deterministically -
# the plan explicitly calls for rules (not the LLM) on these tiers.
_DIRECT_RELIABILITY_TIERS = {SourceReliability.OFFICIAL, SourceReliability.HIGH}

# Sentinel distinguishing "no llm_client argument passed" (build one from
# the environment) from "llm_client=None passed explicitly" (force
# rule-based-only, used by tests that must stay hermetic).
_UNSET = object()


def compute_confidence(signal: NormalizedSignal, affected_entities: list[str]) -> float:
    """Confidence 0-1 (plan section 4.4): official/high-reliability sources
    score higher, a resolved location/entity raises confidence, a signal
    with neither lowers it, and simulated sources are capped so they never
    look more trustworthy than real data."""
    confidence = _RELIABILITY_CONFIDENCE_BASE.get(signal.source_reliability, 0.5)
    if not signal.country_hint:
        confidence -= 0.15
    if affected_entities:
        confidence += 0.05
    else:
        confidence -= 0.1
    if signal.is_simulated:
        confidence = min(confidence, 0.6)
    return round(max(0.05, min(confidence, 0.99)), 2)


def _build_llm_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic

        return anthropic.Anthropic(api_key=api_key)
    except Exception:  # noqa: BLE001 - LLM availability must never break extraction
        logger.warning("Anthropic client unavailable; using rule-based extraction only", exc_info=True)
        return None


def _load_prompt_template() -> str:
    try:
        return _PROMPT_PATH.read_text(encoding="utf-8")
    except OSError:
        logger.warning("Prompt template missing at %s; LLM extraction disabled", _PROMPT_PATH)
        return ""


def _render_prompt(template: str, signal: NormalizedSignal) -> str:
    replacements = {
        "{{TITLE}}": signal.title or "(no title)",
        "{{RAW_TEXT}}": signal.raw_text or "",
        "{{SOURCE_NAME}}": signal.source_name,
        "{{SOURCE_RELIABILITY}}": str(signal.source_reliability),
        "{{LOCATION_HINT}}": signal.country_hint or "unknown",
        "{{PUBLISHED_AT}}": signal.published_at.isoformat() if signal.published_at else "unknown",
    }
    prompt = template
    for placeholder, value in replacements.items():
        prompt = prompt.replace(placeholder, value)
    return prompt


def _first_balanced_json_object(text: str) -> str | None:
    """Returns the substring spanning the first `{` to its matching `}`,
    tracking brace depth - unlike a greedy `\\{.*\\}` regex, this doesn't
    swallow unrelated braces in any prose the model adds before/after the
    JSON object (real models don't always honor a "no prose" instruction)."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def _extract_json_object(text: str) -> dict:
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    candidates = [fenced.group(1)] if fenced else []
    balanced = _first_balanced_json_object(text)
    if balanced:
        candidates.append(balanced)

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc
    raise ValueError("No JSON object found in LLM response") from last_error


class EventExtractionAgent:
    """Converts `NormalizedSignal` records into `ExtractionResult`s."""

    def __init__(
        self,
        digital_twin: DigitalTwinService | None = None,
        llm_client=_UNSET,
        llm_model: str | None = None,
    ):
        self.digital_twin = digital_twin or _load_default_digital_twin()
        self.entity_resolver = EntityResolutionAgent(self.digital_twin)
        self.llm_client = _build_llm_client() if llm_client is _UNSET else llm_client
        self.llm_model = llm_model or os.getenv("LLM_MODEL", "claude-sonnet-5")
        self._prompt_template = _load_prompt_template()
        self._event_sequence: dict[int, int] = {}

    def _next_event_id(self, detected_at: datetime) -> str:
        year = detected_at.year
        self._event_sequence[year] = self._event_sequence.get(year, 0) + 1
        return f"EVT-{year}-{self._event_sequence[year]:04d}"

    def reset_event_sequence(self) -> None:
        """Clears the per-year event-id counter.

        A caller that treats each `extract_batch` run as a full refresh of
        current state (e.g. `api/routes/events.py::run_extraction_pipeline`,
        which replaces the event store rather than appending to it) should
        call this first so ids restart at 0001 instead of climbing forever
        across repeated runs."""
        self._event_sequence.clear()

    def _resolve_entities_and_location(self, signal: NormalizedSignal):
        affected = self.entity_resolver.resolve(signal)
        affected = self.entity_resolver.expand_via_routes(affected)
        coordinates = signal.geo_hint or self.entity_resolver.resolve_coordinates(affected)
        return affected, coordinates

    def extract(self, signal: NormalizedSignal) -> ExtractionResult:
        try:
            if signal.source_reliability in _DIRECT_RELIABILITY_TIERS:
                event = self._rule_based_extract(signal)
                method = "official_alert_direct"
            elif self.llm_client is not None and self._prompt_template:
                try:
                    event = self._llm_extract(signal)
                    method = "llm"
                except Exception as exc:  # noqa: BLE001 - must fall back, never raise
                    logger.warning("LLM extraction failed for signal %s: %s", signal.signal_id, exc)
                    event = self._rule_based_extract(signal)
                    method = "rule_based_fallback"
            else:
                event = self._rule_based_extract(signal)
                method = "rule_based_fallback"

            if event is None:
                return ExtractionResult(
                    signal_id=signal.signal_id,
                    event=None,
                    extraction_method=method,
                    succeeded=False,
                    error_message="No event type could be classified for this signal",
                )
            return ExtractionResult(
                signal_id=signal.signal_id, event=event, extraction_method=method, succeeded=True
            )
        except Exception as exc:  # noqa: BLE001 - a single bad signal must not stop the batch
            logger.exception("Event extraction failed for signal %s", signal.signal_id)
            return ExtractionResult(
                signal_id=signal.signal_id,
                event=None,
                extraction_method="error",
                succeeded=False,
                error_message=str(exc),
            )

    def extract_batch(self, signals: list[NormalizedSignal]) -> list[ExtractionResult]:
        results = [self.extract(signal) for signal in signals]
        self._apply_corroboration_boost(results)
        return results

    def _apply_corroboration_boost(self, results: list[ExtractionResult]) -> None:
        """Confidence input from plan section 4.4: "multiple independent
        sources increase confidence." Corroboration can only be observed at
        batch scope (one signal alone has no visibility into others), so
        this runs as a post-pass over a completed `extract_batch` call
        rather than inside `compute_confidence`, which stays single-signal.
        Groups successful events by (event_type, affected entity) and bumps
        confidence for any group whose members came from >1 distinct source.
        """
        groups: dict[tuple, list[RiskEvent]] = {}
        for result in results:
            if not result.succeeded or result.event is None:
                continue
            entity_ids = result.event.affected_entities or [None]
            for entity_id in entity_ids:
                groups.setdefault((result.event.event_type, entity_id), []).append(result.event)

        boosted: set[int] = set()
        for events in groups.values():
            distinct_sources = {event.source_name for event in events}
            if len(distinct_sources) < 2:
                continue
            for event in events:
                if id(event) in boosted:
                    continue
                boosted.add(id(event))
                event.confidence = round(min(event.confidence + 0.1, 0.99), 2)

    def _rule_based_extract(self, signal: NormalizedSignal) -> RiskEvent | None:
        event_type = event_classifier.classify_event_type(signal)
        if event_type is None:
            return None

        text = f"{signal.title or ''} {signal.raw_text or ''}"
        severity = event_classifier.estimate_severity(event_type, text)
        affected, coordinates = self._resolve_entities_and_location(signal)
        confidence = compute_confidence(signal, affected)
        scenario_triggers = event_classifier.get_scenario_triggers(event_type, affected)

        return RiskEvent(
            event_id=self._next_event_id(signal.detected_at),
            event_type=event_type,
            commodity_type=signal.commodity_type or CommodityType.CRUDE_OIL,
            title=signal.title or f"{event_type} detected via {signal.source_name}",
            summary=(signal.raw_text or "")[:500] or f"{event_type} detected via {signal.source_name}.",
            published_at=signal.published_at,
            detected_at=signal.detected_at,
            source_name=signal.source_name,
            source_reliability=signal.source_reliability,
            location_name=signal.country_hint,
            coordinates=coordinates,
            affected_entities=affected,
            severity=severity,
            confidence=confidence,
            scenario_triggers=scenario_triggers,
            evidence_urls=[signal.url] if signal.url else [],
            is_simulated=signal.is_simulated,
        )

    def _llm_extract(self, signal: NormalizedSignal) -> RiskEvent:
        prompt = _render_prompt(self._prompt_template, signal)
        response = self.llm_client.messages.create(
            model=self.llm_model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = "".join(
            block.text for block in getattr(response, "content", []) if getattr(block, "type", None) == "text"
        )
        payload = _extract_json_object(raw_text)

        event_type = payload.get("event_type")
        if not event_type:
            raise ValueError("LLM response missing 'event_type'")

        # Everything the model isn't well-positioned to know (entity ids,
        # coordinates, confidence, scenario triggers) is always computed
        # deterministically, regardless of extraction method.
        affected, coordinates = self._resolve_entities_and_location(signal)
        text_for_severity = f"{signal.title or ''} {signal.raw_text or ''}"
        default_severity = event_classifier.estimate_severity(event_type, text_for_severity)

        raw_severity = payload.get("severity")
        try:
            severity = int(raw_severity) if raw_severity is not None else default_severity
        except (TypeError, ValueError):
            severity = default_severity
        severity = max(1, min(5, severity))

        return RiskEvent(
            event_id=self._next_event_id(signal.detected_at),
            event_type=event_type,
            commodity_type=payload.get("commodity_type") or signal.commodity_type or CommodityType.CRUDE_OIL,
            title=payload.get("title") or signal.title or f"{event_type} detected via {signal.source_name}",
            summary=payload.get("summary") or (signal.raw_text or "")[:500],
            published_at=signal.published_at,
            detected_at=signal.detected_at,
            source_name=signal.source_name,
            source_reliability=signal.source_reliability,
            location_name=signal.country_hint,
            coordinates=coordinates,
            affected_entities=affected,
            severity=severity,
            confidence=compute_confidence(signal, affected),
            scenario_triggers=event_classifier.get_scenario_triggers(event_type, affected),
            evidence_urls=[signal.url] if signal.url else [],
            is_simulated=bool(payload.get("is_simulated", signal.is_simulated)),
        )


_default_digital_twin: DigitalTwinService | None = None


def _load_default_digital_twin() -> DigitalTwinService:
    global _default_digital_twin
    if _default_digital_twin is None:
        service = DigitalTwinService()
        service.load_seed_data()
        _default_digital_twin = service
    return _default_digital_twin
