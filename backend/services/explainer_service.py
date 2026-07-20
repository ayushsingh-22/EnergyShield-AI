"""Explanation generation for risk and recommendations (Phase 11)."""

from __future__ import annotations

from models.recommendation_schema import Recommendation
from models.risk_schema import RiskScore
from services.event_service import EventService


class ExplainerService:
    """Turns a risk score or recommendation into a plain-language
    explanation with its supporting evidence, so a frontend
    `ExplainabilityPanel` can show "why" without the viewer needing to
    read raw scores, Cypher output, or JSON assumption lists directly."""

    def __init__(self, event_service: EventService | None = None):
        self._event_service = event_service

    def explain_risk_score(self, score: RiskScore) -> dict[str, object]:
        evidence_events = []
        if self._event_service is not None:
            for event_id in score.evidence_event_ids:
                event = self._event_service.get_event(event_id)
                if event is not None:
                    evidence_events.append(event)

        trend = f", up {score.delta} from the previous score" if score.delta else ""
        return {
            "entity_id": score.entity_id,
            "risk_level": score.risk_level,
            "risk_score": score.risk_score,
            "summary": f"{score.entity_id} is {score.risk_level} risk ({score.risk_score}/100){trend}.",
            "top_drivers": list(score.top_drivers),
            "evidence_events": [
                {
                    "event_id": event.event_id,
                    "title": event.title,
                    "severity": event.severity,
                    "source_name": event.source_name,
                    "source_reliability": event.source_reliability,
                }
                for event in evidence_events
            ],
            "confidence": score.confidence,
        }

    def explain_recommendation(self, recommendation: Recommendation) -> dict[str, object]:
        top_option = recommendation.ranked_options[0] if recommendation.ranked_options else None
        return {
            "recommendation_id": recommendation.recommendation_id,
            "scenario_id": recommendation.scenario_id,
            "summary": (
                f"{len(recommendation.ranked_options)} procurement option(s) ranked for "
                f"scenario {recommendation.scenario_id}."
            ),
            "top_option_reason": top_option.reason if top_option else None,
            "spr_reason": recommendation.spr_plan.reason if recommendation.spr_plan else None,
            "assumptions": [assumption.description for assumption in recommendation.assumptions],
            "confidence": recommendation.confidence,
            "audit_id": recommendation.audit_id,
        }
