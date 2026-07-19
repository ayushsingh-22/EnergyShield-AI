from orchestration.event_bus import EventBus


def test_publish_delivers_to_subscribers():
    bus = EventBus(redis_url="redis://nonexistent-host:6399/0")
    received = []
    bus.subscribe("topic.a", lambda payload: received.append(payload))

    bus.publish("topic.a", {"x": 1})

    assert received == [{"x": 1}]


def test_publish_with_no_subscribers_does_not_raise():
    bus = EventBus(redis_url="redis://nonexistent-host:6399/0")
    bus.publish("topic.unused", {"x": 1})


def test_one_bad_subscriber_does_not_block_others():
    bus = EventBus(redis_url="redis://nonexistent-host:6399/0")
    received = []

    def bad_handler(payload):
        raise RuntimeError("boom")

    bus.subscribe("topic.a", bad_handler)
    bus.subscribe("topic.a", lambda payload: received.append(payload))

    bus.publish("topic.a", {"x": 1})

    assert received == [{"x": 1}]


def test_unreachable_redis_does_not_raise():
    bus = EventBus(redis_url="redis://nonexistent-host:6399/0")
    # First publish triggers (and caches) the failed Redis connectivity
    # check; must degrade silently rather than raising.
    bus.publish("topic.a", {"x": 1})
    assert bus._redis_client is None
