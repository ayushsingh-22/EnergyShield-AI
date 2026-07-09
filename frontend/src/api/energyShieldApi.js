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
