"""Tracks model versions, training data range, metrics, owner, and deployment status (Phase 13, section 13.7)."""

from __future__ import annotations

from models.learning_schema import ModelVersion, ModelVersionStatus


class ModelRegistry:
    """In-memory model/rule-version registry (section 13.7). Never
    deletes or mutates an archived version's recorded metrics - only its
    `status` transitions - per the continuous-learning governance rule in
    docs/CONTINUOUS_LEARNING.md: activating a new version must not
    retroactively change what an already-generated scenario/recommendation
    looked like."""

    def __init__(self) -> None:
        self._versions: dict[str, ModelVersion] = {}

    def register(self, version: ModelVersion) -> ModelVersion:
        self._versions[version.model_id] = version
        return version

    def get(self, model_id: str) -> ModelVersion | None:
        return self._versions.get(model_id)

    def list_all(self) -> list[ModelVersion]:
        return list(self._versions.values())

    def get_active(self, model_name: str) -> ModelVersion | None:
        for version in self._versions.values():
            if version.model_name == model_name and version.status == ModelVersionStatus.ACTIVE.value:
                return version
        return None

    def activate(self, model_id: str) -> ModelVersion:
        """Promotes `model_id` to ACTIVE and archives any other ACTIVE
        version of the same model - exactly one active version per model
        name at a time - without touching either version's stored metrics
        (section 13.7, step 2: "mark version as candidate/active/archived")."""
        version = self._versions.get(model_id)
        if version is None:
            raise KeyError(f"Unknown model version '{model_id}'")

        for other in self._versions.values():
            if other.model_name == version.model_name and other.status == ModelVersionStatus.ACTIVE.value:
                other.status = ModelVersionStatus.ARCHIVED.value

        version.status = ModelVersionStatus.ACTIVE.value
        return version


_default_registry: ModelRegistry | None = None


def get_model_registry() -> ModelRegistry:
    """Returns the process-wide `ModelRegistry` singleton."""
    global _default_registry
    if _default_registry is None:
        _default_registry = ModelRegistry()
    return _default_registry
