import * as mock from './mockData'
import { humanize } from '../utils/format'

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

export async function getEntityNames() {
  if (USE_MOCK_DATA) return mock.mockEntityNames
  return request('/digital-twin/names')
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

export async function getEntityNeighborhood(entityId) {
  if (USE_MOCK_DATA) return mock.mockGraphNeighborhood
  return request(`/graph/entity/${encodeURIComponent(entityId)}`)
}

export async function queryImpact(entityId, maxHops = 2) {
  if (USE_MOCK_DATA) return mock.mockGraphImpact
  return request('/graph/query-impact', {
    method: 'POST',
    body: JSON.stringify({ entity_id: entityId, max_hops: maxHops }),
  })
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
      title: `EnergyShield Executive Brief - ${humanize('HORMUZ_PARTIAL_CLOSURE')}`,
      executive_summary:
        `${humanize('CRUDE_OIL')} disruption scenario ${humanize('HORMUZ_PARTIAL_CLOSURE')} places 31% of supply at risk with an estimated 9-day delay.`,
      report_markdown: mock.mockReportMarkdown,
      top_actions: mock.mockRecommendation.ranked_options.map((option) => option.reason),
      spr_action: mock.mockRecommendation.spr_plan,
      audit_id: mock.mockRecommendation.audit_id,
      assumptions: [...mock.mockScenarioResult.assumptions, ...mock.mockRecommendation.assumptions],
      is_simulated: true,
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

export async function getRiskHistory(entityId) {
  if (USE_MOCK_DATA) return mock.mockRiskHistory
  return request(`/risk/history/${encodeURIComponent(entityId)}`)
}

export async function getAuditTrail(entityId) {
  if (USE_MOCK_DATA) return mock.mockAuditTrail.filter((entry) => entry.entity_id === entityId)
  return request(`/audit/${encodeURIComponent(entityId)}`)
}

export async function getLearningCases() {
  if (USE_MOCK_DATA) return mock.mockLearningCases
  return request('/learning/cases')
}

export async function runBacktest(payload = {}) {
  if (USE_MOCK_DATA) return mock.mockBacktestReport
  return request('/learning/backtest', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function submitFeedback(payload) {
  if (USE_MOCK_DATA) return { ...mock.mockFeedbackEntry, ...payload }
  return request('/learning/feedback', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function getModels() {
  if (USE_MOCK_DATA) return mock.mockModelVersions
  return request('/learning/models')
}

export async function activateModel(modelId) {
  if (USE_MOCK_DATA) return { ...mock.mockModelVersions[0], model_id: modelId, status: 'ACTIVE' }
  return request(`/learning/models/${encodeURIComponent(modelId)}/activate`, { method: 'POST' })
}

export async function getCommodityEntities(commodityType) {
  if (USE_MOCK_DATA) return mock.mockCommodityEntities
  return request(`/commodities/${encodeURIComponent(commodityType)}/entities`)
}

export async function getCommodityRisk(commodityType) {
  if (USE_MOCK_DATA) return mock.mockCorridorRisk
  return request(`/commodities/${encodeURIComponent(commodityType)}/risk`)
}

export async function getCommodityScenarios(commodityType) {
  if (USE_MOCK_DATA) return mock.mockCommodities.find((c) => c.commodity_type === commodityType)?.scenario_template_ids ?? []
  return request(`/commodities/${encodeURIComponent(commodityType)}/scenarios`)
}

export async function runCommodityScenario(commodityType, payload) {
  if (USE_MOCK_DATA) return { ...mock.mockScenarioResult, commodity_type: commodityType }
  return request(`/commodities/${encodeURIComponent(commodityType)}/scenarios/run`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function getCommodityRecommendation(commodityType, scenarioId) {
  if (USE_MOCK_DATA) return mock.mockRecommendation
  return request(`/commodities/${encodeURIComponent(commodityType)}/recommendations/${encodeURIComponent(scenarioId)}`)
}
