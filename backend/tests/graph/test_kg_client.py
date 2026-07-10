from graph.kg_client import KGClient


def test_run_query_against_unreachable_neo4j_returns_empty_list():
    client = KGClient(uri="bolt://localhost:1", unavailable_retry_seconds=30.0)

    result = client.run_query("MATCH (n) RETURN n")

    assert result == []


def test_run_query_backs_off_after_first_failure(monkeypatch):
    """After the first connection failure, subsequent calls within the
    backoff window must not attempt a new connection or log again - this
    is what turns "one warning per query" into "one warning per outage"."""
    client = KGClient(uri="bolt://localhost:1", unavailable_retry_seconds=30.0)
    client.run_query("MATCH (n) RETURN n")  # first failure - establishes backoff

    call_count = 0

    def _fail_if_called(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise AssertionError("should not attempt a connection while in backoff")

    monkeypatch.setattr(client, "_get_driver", _fail_if_called)

    result = client.run_query("MATCH (n) RETURN n")

    assert result == []
    assert call_count == 0


def test_run_query_retries_after_backoff_window_expires(monkeypatch):
    client = KGClient(uri="bolt://localhost:1", unavailable_retry_seconds=30.0)
    client.run_query("MATCH (n) RETURN n")  # first failure

    # Simulate the backoff window having elapsed.
    client._unavailable_since -= 31.0

    def _fail_again(*args, **kwargs):
        raise ConnectionError("still down")

    monkeypatch.setattr(client, "_get_driver", _fail_again)

    result = client.run_query("MATCH (n) RETURN n")

    assert result == []
    assert client._unavailable_since is not None


def test_health_check_failure_does_not_raise():
    client = KGClient(uri="bolt://localhost:1")
    assert client.health() is False
