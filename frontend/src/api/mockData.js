export const mockHealth = {
  status: 'ok',
  service: 'energyshield-backend',
  version: '0.1.0',
  checked_at: '2026-07-06T09:00:00Z',
}

export const mockDataFreshness = [
  {
    source_name: 'gdelt',
    last_successful_fetch_at: '2026-07-09T09:00:00Z',
    last_attempt_at: '2026-07-09T09:00:00Z',
    is_healthy: true,
    consecutive_failures: 0,
    reliability_tier: 'MEDIUM',
  },
  {
    source_name: 'maritime_alerts',
    last_successful_fetch_at: '2026-07-09T09:05:00Z',
    last_attempt_at: '2026-07-09T09:05:00Z',
    is_healthy: true,
    consecutive_failures: 0,
    reliability_tier: 'HIGH',
  },
  {
    source_name: 'sanctions',
    last_successful_fetch_at: '2026-07-09T08:00:00Z',
    last_attempt_at: '2026-07-09T08:00:00Z',
    is_healthy: true,
    consecutive_failures: 0,
    reliability_tier: 'OFFICIAL',
  },
]

export const mockDigitalTwinMap = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { entity_id: 'EXP_BAS', name: 'Basra Terminal', entity_type: 'ExportPort' },
      geometry: { type: 'Point', coordinates: [47.8, 29.9] },
    },
    {
      type: 'Feature',
      properties: { entity_id: 'IMP_JAM', name: 'Jamnagar Port', entity_type: 'ImportPort' },
      geometry: { type: 'Point', coordinates: [70.0, 22.5] },
    },
    {
      type: 'Feature',
      properties: { entity_id: 'REF_JAM', name: 'Reliance Jamnagar', entity_type: 'Refinery' },
      geometry: { type: 'Point', coordinates: [69.8, 22.4] },
    },
    {
      type: 'Feature',
      properties: { entity_id: 'SPR_PAD', name: 'Padur SPR', entity_type: 'SPR' },
      geometry: { type: 'Point', coordinates: [74.8, 13.1] },
    },
    {
      type: 'Feature',
      properties: { entity_id: 'RT_BAS_JAM', name: 'Basra to Jamnagar', entity_type: 'ShippingRoute' },
      geometry: { type: 'LineString', coordinates: [[47.8, 29.9], [56.2, 26.5], [70.0, 22.5]] },
    },
    {
      type: 'Feature',
      properties: { entity_id: 'CHK_HORMUZ', name: 'Strait of Hormuz', entity_type: 'Chokepoint' },
      geometry: { type: 'Polygon', coordinates: [[[56.0, 26.0], [56.5, 26.0], [56.5, 26.5], [56.0, 26.5], [56.0, 26.0]]] },
    },
  ],
}

export const mockDigitalTwinExposure = {
  total_supplier_exposure_percent: 100,
  route_exposure_percent: { RT_BAS_JAM: 28.1 },
  chokepoint_exposure_percent: { CHK_HORMUZ: 62.4 },
  total_refineries: 3,
  total_spr_capacity_mmbbl: 39,
}

export const mockRefineriesExposed = [
  {
    entity_id: 'REF_JAM',
    name: 'Reliance Jamnagar',
    risk_level: 'HIGH',
    via_route_id: 'RT_BAS_JAM',
  },
]

export const mockAlternativeSuppliers = [
  {
    entity_id: 'SUP_KSA',
    name: 'Saudi Arabia',
    region: 'Middle East',
    import_share_percent: 18.7,
    crude_grade_ids: ['GRADE_ARAB_LIGHT'],
  },
  {
    entity_id: 'SUP_UAE',
    name: 'United Arab Emirates',
    region: 'Middle East',
    import_share_percent: 9.4,
    crude_grade_ids: ['GRADE_MURBAN'],
  },
]

export const mockLatestEvents = []
export const mockCorridorRisk = []
export const mockSupplierRisk = []
export const mockScenarioResult = null
export const mockRecommendation = null
