"""Stores curated historical disruption cases with trigger events, outcomes, and source quality (Phase 13, section 13.1)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from models.learning_schema import HistoricalCase

logger = logging.getLogger(__name__)

# Anchored to this file's location (not the process cwd) - the same
# convention `services/digital_twin_service.py` uses for its own seed
# data - so it resolves correctly regardless of where the app is run from.
_DEFAULT_CASES_PATH = Path(__file__).resolve().parents[2] / "data" / "seeds" / "demo_disruption_cases.json"


class DisruptionCaseLibrary:
    """Searchable store of curated historical disruption cases (section
    13.1). Seeded from `data/seeds/demo_disruption_cases.json` - five
    illustrative cases (2023-24 Red Sea/Houthi attacks, 2019 Hormuz tanker
    incidents, 2022 Russian crude reroute, 2008-11 Gulf of Aden piracy
    surge, 2021 Suez/Ever Given blockage), each explicitly marked
    `is_simulated` per Planning Principle #9."""

    def __init__(self, cases_path: str | Path = _DEFAULT_CASES_PATH):
        self.cases_path = Path(cases_path)
        self._cases: dict[str, HistoricalCase] = {}

    def load_seed_data(self) -> None:
        if not self.cases_path.exists():
            logger.warning("Disruption case seed file not found at %s", self.cases_path)
            return
        raw_cases = json.loads(self.cases_path.read_text())
        for raw in raw_cases:
            case = HistoricalCase(**raw)
            self._cases[case.case_id] = case
        logger.info("Loaded %d historical disruption case(s).", len(self._cases))

    def add_case(self, case: HistoricalCase) -> HistoricalCase:
        self._cases[case.case_id] = case
        return case

    def get_case(self, case_id: str) -> HistoricalCase | None:
        return self._cases.get(case_id)

    def get_all(self) -> list[HistoricalCase]:
        return list(self._cases.values())
