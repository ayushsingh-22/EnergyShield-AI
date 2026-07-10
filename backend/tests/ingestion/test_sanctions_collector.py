from ingestion.sanctions_collector import SanctionsCollector, _SEEDED_SANCTIONS_SNAPSHOT


def test_first_fetch_surfaces_the_full_seeded_snapshot_as_new():
    collector = SanctionsCollector()

    records = collector.fetch()

    assert len(records) == len(_SEEDED_SANCTIONS_SNAPSHOT)


def test_second_fetch_on_same_instance_reports_no_new_deltas():
    collector = SanctionsCollector()
    collector.fetch()

    records = collector.fetch()

    assert records == []


def test_two_independent_instances_each_see_the_full_snapshot():
    """Two consumers (e.g. the freshness bootstrap and the events pipeline)
    each hold their own SanctionsCollector instance and must each see the
    full snapshot once, rather than racing each other for who "claims" it."""
    first_consumer = SanctionsCollector()
    second_consumer = SanctionsCollector()

    assert len(first_consumer.fetch()) == len(_SEEDED_SANCTIONS_SNAPSHOT)
    assert len(second_consumer.fetch()) == len(_SEEDED_SANCTIONS_SNAPSHOT)
