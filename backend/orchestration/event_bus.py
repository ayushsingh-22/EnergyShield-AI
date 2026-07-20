"""Lightweight event bus or Redis stream wrapper connecting orchestration stages."""

from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)

Handler = Callable[[dict[str, Any]], None]


class EventBus:
    """In-process publish/subscribe bus connecting orchestration stages
    (sections 10.2-10.4: signal -> extraction -> risk -> scenario ->
    recommendation). In-process delivery is always synchronous and never
    depends on Redis; every publish is *also* best-effort mirrored to a
    Redis stream when `REDIS_URL` is reachable, so an external process
    (e.g. a future separate worker pool) can observe the same events -
    same graceful-degradation contract as `graph/kg_client.py`."""

    def __init__(self, redis_url: str | None = None):
        self._subscribers: dict[str, list[Handler]] = defaultdict(list)
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis_client = None
        self._redis_checked = False

    def subscribe(self, topic: str, handler: Handler) -> None:
        self._subscribers[topic].append(handler)

    def publish(self, topic: str, payload: dict[str, Any]) -> None:
        self._mirror_to_redis(topic, payload)
        for handler in list(self._subscribers.get(topic, [])):
            try:
                handler(payload)
            except Exception:  # noqa: BLE001 - one bad subscriber must not break the pipeline
                logger.exception("Event bus handler for topic '%s' failed", topic)

    def _get_redis(self):
        if self._redis_checked:
            return self._redis_client
        self._redis_checked = True
        try:
            import redis

            client = redis.from_url(self._redis_url, socket_connect_timeout=1)
            client.ping()
            self._redis_client = client
        except Exception:  # noqa: BLE001 - external service, must not crash caller
            logger.info("Redis unreachable at %s; event bus runs in-process only.", self._redis_url)
            self._redis_client = None
        return self._redis_client

    def _mirror_to_redis(self, topic: str, payload: dict[str, Any]) -> None:
        client = self._get_redis()
        if client is None:
            return
        try:
            client.xadd(f"energyshield:{topic}", {"payload": json.dumps(payload, default=str)})
        except Exception:  # noqa: BLE001 - external service, must not crash caller
            logger.warning("Failed to mirror event to Redis stream for topic '%s'", topic, exc_info=True)


_default_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Returns the process-wide `EventBus` singleton."""
    global _default_bus
    if _default_bus is None:
        _default_bus = EventBus()
    return _default_bus
