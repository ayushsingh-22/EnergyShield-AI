"""Runs data collectors on configured refresh intervals from the source registry (Phase 10, section 10.1)."""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class ScheduledJob:
    name: str
    interval_seconds: float
    func: Callable[[], object]
    last_run_monotonic: float = field(default=0.0)


class Scheduler:
    """A single background thread that runs each registered job once its
    interval has elapsed.

    Deliberately not a distributed task queue (Celery/APScheduler): this
    is a single-instance FastAPI app with an in-memory service layer, so a
    plain timer loop is enough and matches the "lightweight" language the
    plan uses for `event_bus.py` too - and does not need a new dependency
    beyond the standard library.
    """

    def __init__(self, tick_seconds: float = 1.0):
        self._jobs: dict[str, ScheduledJob] = {}
        self._tick_seconds = tick_seconds
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def add_job(self, name: str, interval_seconds: float, func: Callable[[], object]) -> None:
        self._jobs[name] = ScheduledJob(name=name, interval_seconds=interval_seconds, func=func)

    def run_due_jobs(self, now: float | None = None) -> list[str]:
        """Runs every job whose interval has elapsed since its last run.
        Exposed standalone (not only reachable via the background thread)
        so it is directly unit-testable and callable from a manual
        "refresh now" trigger without waiting on the clock."""
        now = now if now is not None else time.monotonic()
        ran = []
        for job in self._jobs.values():
            if now - job.last_run_monotonic >= job.interval_seconds:
                job.last_run_monotonic = now
                try:
                    job.func()
                    ran.append(job.name)
                except Exception:  # noqa: BLE001 - one bad job must not stop the scheduler
                    logger.exception("Scheduled job '%s' failed", job.name)
        return ran

    def start(self) -> None:
        if self._thread is not None:
            return
        self._stop_event.clear()

        def _loop() -> None:
            while not self._stop_event.is_set():
                self.run_due_jobs()
                self._stop_event.wait(self._tick_seconds)

        self._thread = threading.Thread(target=_loop, name="energyshield-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None


_default_scheduler: Scheduler | None = None


def get_scheduler() -> Scheduler:
    """Returns the process-wide `Scheduler` singleton."""
    global _default_scheduler
    if _default_scheduler is None:
        _default_scheduler = Scheduler()
    return _default_scheduler


def configure_default_jobs(scheduler: Scheduler | None = None) -> Scheduler:
    """Registers the Phase 10 end-to-end pipeline as a recurring job at
    `DATA_REFRESH_INTERVAL_MINUTES` (default 15, per .env.example)."""
    from orchestration.workflows import run_full_pipeline

    scheduler = scheduler or get_scheduler()
    interval_minutes = float(os.getenv("DATA_REFRESH_INTERVAL_MINUTES", "15"))
    scheduler.add_job("full_pipeline", interval_minutes * 60, run_full_pipeline)
    return scheduler
