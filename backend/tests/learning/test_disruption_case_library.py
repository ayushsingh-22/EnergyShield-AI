from learning.disruption_case_library import DisruptionCaseLibrary


def test_load_seed_data_loads_demo_cases():
    library = DisruptionCaseLibrary()
    library.load_seed_data()

    cases = library.get_all()

    # Phase 13 validation: "at least 5 curated cases or seeded examples."
    assert len(cases) >= 5
    assert library.get_case("CASE-REDSEA-2024-001") is not None
    assert all(case.is_simulated for case in cases)


def test_get_unknown_case_returns_none():
    library = DisruptionCaseLibrary()
    library.load_seed_data()
    assert library.get_case("UNKNOWN") is None
