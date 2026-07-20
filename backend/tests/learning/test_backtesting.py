from learning.backtesting import run_backtest
from learning.disruption_case_library import DisruptionCaseLibrary


def test_run_backtest_over_seeded_cases_produces_metrics():
    library = DisruptionCaseLibrary()
    library.load_seed_data()

    report = run_backtest(library.get_all())

    assert len(report.case_results) == len(library.get_all())
    assert 0.0 <= report.precision <= 1.0
    assert 0.0 <= report.recall <= 1.0
    assert 0.0 <= report.false_alarm_rate <= 1.0
    assert 0.0 <= report.missed_event_rate <= 1.0


def test_backtest_resolves_scenario_type_for_known_corridors():
    library = DisruptionCaseLibrary()
    library.load_seed_data()

    report = run_backtest(library.get_all())

    redsea_result = next(r for r in report.case_results if r.case_id == "CASE-REDSEA-2024-001")
    assert redsea_result.scenario_type == "RED_SEA_SHIPPING_DISRUPTION"
    assert redsea_result.predicted_supply_at_risk_percent is not None
