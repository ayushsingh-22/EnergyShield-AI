from datetime import datetime, timezone

from models.core_schema import CommodityType, EntityType, RiskLevel
from models.risk_schema import RiskScore
from workers.risk_worker import run_risk_scoring_job


class _FakeRiskService:
    def __init__(self, corridors, suppliers):
        self._corridors = corridors
        self._suppliers = suppliers
        self.refreshed = False

    def refresh(self):
        self.refreshed = True

    def get_corridors(self):
        return self._corridors

    def get_suppliers(self):
        return self._suppliers


def _score(entity_id, entity_type) -> RiskScore:
    return RiskScore(
        entity_id=entity_id,
        entity_type=entity_type,
        commodity_type=CommodityType.CRUDE_OIL,
        risk_score=50.0,
        risk_level=RiskLevel.MEDIUM,
        confidence=0.8,
        updated_at=datetime.now(timezone.utc),
    )


def test_run_risk_scoring_job_refreshes_and_combines_corridors_and_suppliers():
    corridor = _score("CHK_HORMUZ", EntityType.CHOKEPOINT)
    supplier = _score("SUP_IRQ", EntityType.SUPPLIER_COUNTRY)
    service = _FakeRiskService([corridor], [supplier])

    scores = run_risk_scoring_job(service)

    assert service.refreshed is True
    assert scores == [corridor, supplier]
