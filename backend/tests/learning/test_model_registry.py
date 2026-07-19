from datetime import datetime, timezone

import pytest

from learning.model_registry import ModelRegistry
from models.learning_schema import ModelVersion, ModelVersionStatus


def _version(model_id, status=ModelVersionStatus.CANDIDATE) -> ModelVersion:
    return ModelVersion(
        model_id=model_id,
        model_name="risk-scoring",
        version="0.1",
        status=status,
        trained_at=datetime.now(timezone.utc),
        metrics={"f1": 0.8},
    )


def test_activate_promotes_and_archives_previous_active():
    registry = ModelRegistry()
    registry.register(_version("v1", ModelVersionStatus.ACTIVE))
    registry.register(_version("v2"))

    activated = registry.activate("v2")

    assert activated.status == "ACTIVE"
    assert registry.get("v1").status == "ARCHIVED"
    assert registry.get_active("risk-scoring").model_id == "v2"


def test_activate_unknown_model_raises():
    registry = ModelRegistry()
    with pytest.raises(KeyError):
        registry.activate("unknown")


def test_archived_version_metrics_are_untouched_after_activation():
    registry = ModelRegistry()
    registry.register(_version("v1", ModelVersionStatus.ACTIVE))
    registry.register(_version("v2"))
    registry.activate("v2")
    assert registry.get("v1").metrics == {"f1": 0.8}
