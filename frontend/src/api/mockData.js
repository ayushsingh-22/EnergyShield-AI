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

export const mockLatestEvents = [
  {
    event_id: 'EVT-2026-0001',
    event_type: 'MARITIME_ATTACK',
    commodity_type: 'CRUDE_OIL',
    title: 'Tanker incident reported near Strait of Hormuz',
    summary: 'A tanker was reportedly approached while transiting the Strait of Hormuz.',
    detected_at: '2026-07-09T09:15:00Z',
    source_name: 'maritime_alerts',
    source_reliability: 'HIGH',
    location_name: 'Strait of Hormuz',
    affected_entities: ['CHK_HORMUZ', 'RT_BAS_JAM', 'RT_RAS_MUN'],
    severity: 4,
    confidence: 0.82,
    scenario_triggers: ['HORMUZ_PARTIAL_CLOSURE'],
    is_simulated: false,
  },
  {
    event_id: 'EVT-2026-0002',
    event_type: 'SANCTION_UPDATE',
    commodity_type: 'CRUDE_OIL',
    title: 'New sanctions target shipping entities',
    summary: 'Sanctions were imposed on shipping companies involved in illicit crude transport.',
    detected_at: '2026-07-09T08:00:00Z',
    source_name: 'sanctions',
    source_reliability: 'OFFICIAL',
    location_name: 'Global',
    affected_entities: [],
    severity: 3,
    confidence: 0.95,
    scenario_triggers: ['SANCTIONS_SHOCK'],
    is_simulated: false,
  },
]

export const mockCorridorRisk = [
  {
    entity_id: 'CHK_HORMUZ',
    entity_type: 'CHOKEPOINT',
    commodity_type: 'CRUDE_OIL',
    risk_score: 84,
    risk_level: 'SEVERE',
    previous_score: 71,
    delta: 13,
    top_drivers: ['Maritime alert clustering near Strait of Hormuz'],
    evidence_event_ids: ['EVT-2026-0001'],
    confidence: 0.84,
    assumptions: [{ description: 'Demo heuristic.', is_simulated: true }],
    audit_id: 'AUD-RISK-CHK_HORMUZ',
    updated_at: '2026-07-10T09:00:00Z',
  },
]

export const mockSupplierRisk = [
  {
    entity_id: 'SUP_IRQ',
    entity_type: 'SUPPLIER_COUNTRY',
    commodity_type: 'CRUDE_OIL',
    risk_score: 79,
    risk_level: 'HIGH',
    previous_score: 66,
    delta: 13,
    top_drivers: ['Supplier relies on Hormuz-exposed export flows'],
    evidence_event_ids: ['EVT-2026-0001'],
    confidence: 0.81,
    assumptions: [{ description: 'Demo heuristic.', is_simulated: true }],
    audit_id: 'AUD-RISK-SUP_IRQ',
    updated_at: '2026-07-10T09:00:00Z',
  },
]

export const mockScenarioResult = {
  scenario_id: 'SCN-20260710-0001',
  scenario_type: 'HORMUZ_PARTIAL_CLOSURE',
  commodity_type: 'CRUDE_OIL',
  duration_days: 14,
  supply_at_risk_percent: 31,
  estimated_delay_days: 9,
  freight_cost_impact_percent: 18,
  affected_refineries: [
    {
      refinery_id: 'REF_JAM',
      exposure_level: 'HIGH',
      reason: 'Seeded dependency graph marks Reliance Jamnagar as exposed.',
    },
  ],
  recommended_action_required: true,
  confidence: 0.84,
  assumptions: [{ description: 'Deterministic demo simulation.', is_simulated: true }],
  created_at: '2026-07-10T09:00:00Z',
}

export const mockRecommendation = {
  recommendation_id: 'REC-SCN-20260710-0001',
  scenario_id: 'SCN-20260710-0001',
  commodity_type: 'CRUDE_OIL',
  ranked_options: [
    {
      rank: 1,
      supplier: 'Saudi Arabia',
      route: 'East-West corridor to west coast India',
      estimated_delay_days: 5,
      cost_impact_percent: 15,
      risk_level: 'MEDIUM',
      feasibility_score: 0.82,
      reason: 'Largest near-term alternative with strong substitution fit.',
      action_priority: 'IMMEDIATE',
    },
  ],
  spr_plan: {
    drawdown_required: true,
    start_day: 3,
    drawdown_percent: 18,
    reason: 'Triggered by supply-at-risk threshold.',
  },
  confidence: 0.79,
  assumptions: [{ description: 'Deterministic heuristic ranking.', is_simulated: true }],
  audit_id: 'AUD-REC-SCN-20260710-0001',
  created_at: '2026-07-10T09:05:00Z',
}

export const mockCommodities = [
  {
    commodity_type: 'CRUDE_OIL',
    display_name: 'Crude Oil',
    unit: 'barrel',
    demand_sector_ids: ['Refining', 'Transport'],
    risk_parameters: { status_weight: 1 },
    scenario_template_ids: ['HORMUZ_PARTIAL_CLOSURE', 'RED_SEA_SHIPPING_DISRUPTION'],
  },
  {
    commodity_type: 'LNG',
    display_name: 'Lng',
    unit: 'mmbtu',
    demand_sector_ids: ['Power', 'City gas'],
    risk_parameters: { status_weight: 0.5 },
    scenario_template_ids: ['LNG_SUPPLY_SHOCK'],
  },
]
