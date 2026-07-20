"""Tracks scheduled/background job status for the /api/v1/data/freshness and job monitoring views (Phase 10, section 10.5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from itertools import count
from threading import Lock
from typing import Any


class JobStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass
class JobRun:
    run_id: str
    job_name: str
    status: JobStatus
    started_at: datetime
    finished_at: datetime | None = None
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


class JobStatusTracker:
    """In-memory record of every orchestration job run (section 10.5:
    "show job status and failures"). Kept separate from
    `ingestion.source_registry`'s per-source freshness tracking, which
    covers individual collector fetches - this tracks job-level runs of
    the orchestration pipeline itself (full runs and per-stage worker
    runs)."""

    def __init__(self, max_history_per_job: int = 50):
        self._lock = Lock()
        self._counter = count(1)
        self._history: dict[str, list[JobRun]] = {}
        self._max_history_per_job = max_history_per_job

    def start(self, job_name: str) -> JobRun:
        run = JobRun(
            run_id=f"JOB-{next(self._counter):06d}",
            job_name=job_name,
            status=JobStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )
        with self._lock:
            history = self._history.setdefault(job_name, [])
            history.append(run)
            if len(history) > self._max_history_per_job:
                del history[: len(history) - self._max_history_per_job]
        return run

    def finish(self, run: JobRun, *, error: str | None = None, details: dict[str, Any] | None = None) -> JobRun:
        run.finished_at = datetime.now(timezone.utc)
        run.status = JobStatus.FAILED if error else JobStatus.SUCCESS
        run.error = error
        if details:
            run.details.update(details)
        return run

    def latest(self, job_name: str) -> JobRun | None:
        history = self._history.get(job_name)
        return history[-1] if history else None

    def all_latest(self) -> list[JobRun]:
        return [history[-1] for history in self._history.values() if history]

    def history(self, job_name: str) -> list[JobRun]:
        return list(self._history.get(job_name, []))


_default_tracker: JobStatusTracker | None = None


def get_job_status_tracker() -> JobStatusTracker:
    """Returns the process-wide `JobStatusTracker` singleton."""
    global _default_tracker
    if _default_tracker is None:
        _default_tracker = JobStatusTracker()
    return _default_tracker
