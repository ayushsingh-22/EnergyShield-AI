from learning.feedback_service import FeedbackService
from models.learning_schema import FeedbackAction


def test_submit_and_retrieve_feedback():
    service = FeedbackService()
    service.submit_feedback(recommendation_id="REC-1", useful=True, action_taken=FeedbackAction.ACCEPTED)
    service.submit_feedback(
        recommendation_id="REC-1",
        useful=False,
        action_taken=FeedbackAction.REJECTED,
        rejection_reason="too costly",
    )

    entries = service.get_for_recommendation("REC-1")

    assert len(entries) == 2
    assert entries[1].rejection_reason == "too costly"


def test_usefulness_rate_percent():
    service = FeedbackService()
    service.submit_feedback(recommendation_id="REC-1", useful=True, action_taken=FeedbackAction.ACCEPTED)
    service.submit_feedback(recommendation_id="REC-2", useful=False, action_taken=FeedbackAction.REJECTED)

    assert service.usefulness_rate_percent() == 50.0


def test_usefulness_rate_percent_with_no_feedback_is_zero():
    assert FeedbackService().usefulness_rate_percent() == 0.0
