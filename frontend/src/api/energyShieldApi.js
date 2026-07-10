import * as mock from './mockData'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    throw new Error(`EnergyShield API error ${response.status}: ${path}`)
  }
  return response.json()
}

export async function getHealth() {
  if (USE_MOCK_DATA) return mock.mockHealth
  return request('/health')
}

export async function getDataFreshness() {
  if (USE_MOCK_DATA) return mock.mockDataFreshness
  return request('/data/freshness')
}

export async function getDigitalTwinMap() {
  if (USE_MOCK_DATA) return mock.mockDigitalTwinMap
  return request('/digital-twin/map')
}

export async function getDigitalTwinExposure() {
  if (USE_MOCK_DATA) return mock.mockDigitalTwinExposure
  return request('/digital-twin/exposure')
}

export async function getRefineriesExposed(chokepointId) {
  if (USE_MOCK_DATA) return mock.mockRefineriesExposed
  return request(`/graph/refineries-exposed?chokepoint_id=${encodeURIComponent(chokepointId)}`)
}

export async function getAlternativeSuppliers(supplierId, commodity) {
  if (USE_MOCK_DATA) return mock.mockAlternativeSuppliers
  const search = new URLSearchParams({ supplier_id: supplierId, commodity })
  return request(`/graph/alternative-suppliers?${search.toString()}`)
}

export async function getLatestEvents(limit = 10) {
  if (USE_MOCK_DATA) return mock.mockLatestEvents.slice(0, limit)
  return request(`/events/latest?limit=${encodeURIComponent(limit)}`)
}

export async function getCorridorRisk() {
  if (USE_MOCK_DATA) return mock.mockCorridorRisk
  return request('/risk/corridors')
}

export async function getSupplierRisk() {
  if (USE_MOCK_DATA) return mock.mockSupplierRisk
  return request('/risk/suppliers')
}

export async function runScenario(payload) {
  if (USE_MOCK_DATA) return mock.mockScenarioResult
  return request('/scenarios/run', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function getScenario(scenarioId) {
  if (USE_MOCK_DATA) return mock.mockScenarioResult
  return request(`/scenarios/${encodeURIComponent(scenarioId)}`)
}

export async function getRecommendation(scenarioId) {
  if (USE_MOCK_DATA) return mock.mockRecommendation
  return request(`/recommendations/${encodeURIComponent(scenarioId)}`)
}

export async function generateReport(scenarioId) {
  if (USE_MOCK_DATA) {
    return {
      report_id: 'RPT-SCN-20260710-0001',
      scenario_id: mock.mockScenarioResult.scenario_id,
      recommendation_id: mock.mockRecommendation.recommendation_id,
      title: 'EnergyShield Executive Brief - HORMUZ_PARTIAL_CLOSURE',
    }
  }
  return request('/reports/generate', {
    method: 'POST',
    body: JSON.stringify({ scenario_id: scenarioId }),
  })
}

export async function getCommodities() {
  if (USE_MOCK_DATA) return mock.mockCommodities
  return request('/commodities')
}
