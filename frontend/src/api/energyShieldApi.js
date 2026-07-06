// Thin API client for the EnergyShield backend. Every function returns data
// shaped like the schemas in backend/models/*.py (see docs/API_REFERENCE.md).
// When VITE_USE_MOCK_DATA is true, calls resolve from mockData.js instead of
// hitting the network - this lets frontend pages be built before the
// corresponding backend endpoint exists.

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

// TODO(Phase 1): export async function getDataFreshness()
// TODO(Phase 4): export async function getLatestEvents()
// TODO(Phase 5): export async function getCorridorRisk() / getSupplierRisk()
// TODO(Phase 2): export async function getDigitalTwinMap()
// TODO(Phase 6): export async function runScenario(scenarioRequest)
// TODO(Phase 7): export async function getRecommendation(scenarioId)
