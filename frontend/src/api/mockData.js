// Mock API responses shaped exactly like the backend Pydantic schemas in
// backend/models/*.py and documented in docs/API_REFERENCE.md. Frontend
// pages should be built against this file first, then switched to the live
// backend by flipping VITE_USE_MOCK_DATA to false (see energyShieldApi.js).
//
// Add one mock entry here per endpoint as its page/component is built.
// Keep field names and enum values in sync with the backend schemas -
// this file is the frontend's copy of the frozen API contract.

export const mockHealth = {
  status: 'ok',
  service: 'energyshield-backend',
  version: '0.1.0',
  checked_at: '2026-07-06T09:00:00Z',
}

// TODO(Phase 1): mock GET /data/freshness -> SourceFreshness[]
export const mockDataFreshness = []

// TODO(Phase 4): mock GET /events/latest -> RiskEvent[]
export const mockLatestEvents = []

// TODO(Phase 5): mock GET /risk/corridors and /risk/suppliers
export const mockCorridorRisk = []
export const mockSupplierRisk = []

// TODO(Phase 2): mock GET /digital-twin/map
export const mockDigitalTwinMap = null

// TODO(Phase 6): mock POST /scenarios/run -> ScenarioResult
export const mockScenarioResult = null

// TODO(Phase 7): mock GET /recommendations/{scenario_id} -> Recommendation
export const mockRecommendation = null
