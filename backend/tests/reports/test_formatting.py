from reports.formatting import humanize


def test_humanize_scenario_type():
    assert humanize("HORMUZ_PARTIAL_CLOSURE") == "Hormuz Partial Closure"


def test_humanize_commodity_type():
    assert humanize("CRUDE_OIL") == "Crude Oil"


def test_humanize_keeps_acronym_overrides():
    assert humanize("LNG_SUPPLY_SHOCK") == "LNG Supply Shock"
    assert humanize("OPEC_SUPPLY_CUT") == "OPEC+ Supply Cut"


def test_humanize_single_word():
    assert humanize("HIGH") == "High"


def test_humanize_none_returns_empty_string():
    assert humanize(None) == ""
