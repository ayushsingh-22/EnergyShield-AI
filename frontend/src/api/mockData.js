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

export const mockReportMarkdown = `# EnergyShield Executive Brief - HORMUZ_PARTIAL_CLOSURE

**Report ID:** RPT-SCN-20260710-0001
**Scenario:** SCN-20260710-0001 | **Recommendation:** REC-SCN-20260710-0001

## Executive Summary
CRUDE_OIL disruption scenario HORMUZ_PARTIAL_CLOSURE places **31%** of supply at risk with an estimated **9-day** delay.

## Recommended Actions
1. **Saudi Arabia** via East-West corridor to west coast India - IMMEDIATE

## Strategic Reserve Action
Drawdown recommended: 18% starting day 3.
`

export const mockGraphNeighborhood = {
  nodes: [{ entity_id: 'CHK_HORMUZ', label: 'Chokepoint', properties: { name: 'Strait of Hormuz', risk_level: 'HIGH' } }],
  edges: [
    {
      source_id: 'RT_BAS_JAM',
      target_id: 'CHK_HORMUZ',
      relationship_type: 'TRANSITS',
      properties: {},
      confidence: null,
    },
  ],
  query_description: "Direct relationships for entity 'CHK_HORMUZ'",
}

export const mockGraphImpact = {
  nodes: [
    { entity_id: 'CHK_HORMUZ', label: 'Chokepoint', properties: { name: 'Strait of Hormuz' } },
    { entity_id: 'RT_BAS_JAM', label: 'ShippingRoute', properties: { name: 'Basra to Jamnagar' } },
    { entity_id: 'REF_JAM', label: 'Refinery', properties: { name: 'Reliance Jamnagar' } },
  ],
  edges: [
    { source_id: 'RT_BAS_JAM', target_id: 'CHK_HORMUZ', relationship_type: 'TRANSITS', properties: {}, confidence: null },
    { source_id: 'RT_BAS_JAM', target_id: 'REF_JAM', relationship_type: 'ARRIVES_AT', properties: {}, confidence: null },
  ],
  query_description: "Downstream impact of 'CHK_HORMUZ' within 2 hop(s)",
}

export const mockRiskHistory = [
  {
    entity_id: 'CHK_HORMUZ',
    entity_type: 'CHOKEPOINT',
    commodity_type: 'CRUDE_OIL',
    risk_score: 71,
    risk_level: 'HIGH',
    previous_score: 58,
    delta: 13,
    top_drivers: ['Maritime alert clustering near Strait of Hormuz'],
    evidence_event_ids: ['EVT-2026-0001'],
    confidence: 0.8,
    assumptions: [{ description: 'Demo heuristic.', is_simulated: true }],
    audit_id: 'AUD-RISK-CHK_HORMUZ-1',
    updated_at: '2026-07-09T09:00:00Z',
  },
  { ...mockCorridorRisk[0] },
]

export const mockAuditTrail = [
  {
    audit_id: 'AUD-000001',
    entity_id: 'SCN-20260710-0001',
    entity_type: 'SCENARIO',
    action: 'SCENARIO_RUN',
    actor: 'system',
    timestamp: '2026-07-10T09:00:00Z',
    source_event_ids: ['EVT-2026-0001'],
    model_version: null,
    summary: 'Ran HORMUZ_PARTIAL_CLOSURE scenario (31% supply at risk).',
    details: { confidence: 0.84 },
  },
  {
    audit_id: 'AUD-000002',
    entity_id: 'REC-SCN-20260710-0001',
    entity_type: 'RECOMMENDATION',
    action: 'RECOMMENDATION_GENERATED',
    actor: 'system',
    timestamp: '2026-07-10T09:05:00Z',
    source_event_ids: [],
    model_version: null,
    summary: 'Generated 2 procurement option(s) for SCN-20260710-0001.',
    details: { confidence: 0.79, spr_drawdown_required: true },
  },
]

export const mockLearningCases = [
  {
    case_id: 'CASE-REDSEA-2024-001',
    case_name: 'Red Sea / Bab el-Mandeb shipping disruption (Houthi attacks)',
    commodity_type: 'CRUDE_OIL',
    start_date: '2023-11-19',
    end_date: '2024-06-30',
    trigger_events: ['MARITIME_ATTACK', 'AIS_REROUTING'],
    affected_corridors: ['RED_SEA', 'SUEZ', 'BAB_EL_MANDEB'],
    observed_outcomes: {
      average_delay_days: 10,
      freight_cost_increase_percent: 20,
      route_shift_detected: true,
      price_movement_percent: 5,
    },
    source_notes: 'Illustrative, based on public reporting; not audited historical statistics.',
    is_simulated: true,
  },
  {
    case_id: 'CASE-HORMUZ-2019-001',
    case_name: 'Strait of Hormuz tanker incidents and seizures',
    commodity_type: 'CRUDE_OIL',
    start_date: '2019-05-12',
    end_date: '2019-09-30',
    trigger_events: ['MARITIME_ATTACK', 'POLITICAL_INSTABILITY'],
    affected_corridors: ['HORMUZ'],
    observed_outcomes: {
      average_delay_days: 4,
      freight_cost_increase_percent: 12,
      route_shift_detected: false,
      price_movement_percent: 8,
    },
    source_notes: 'Illustrative, based on public reporting; not audited historical statistics.',
    is_simulated: true,
  },
]

export const mockBacktestReport = {
  run_id: 'BT-20260710120000',
  precision: 0.8,
  recall: 0.75,
  false_alarm_rate: 0.2,
  missed_event_rate: 0.25,
  case_results: [
    {
      case_id: 'CASE-REDSEA-2024-001',
      scenario_type: 'RED_SEA_SHIPPING_DISRUPTION',
      predicted_materially_disruptive: true,
      observed_materially_disruptive: true,
      predicted_supply_at_risk_percent: 18.2,
      predicted_confidence: 0.74,
    },
    {
      case_id: 'CASE-HORMUZ-2019-001',
      scenario_type: 'HORMUZ_PARTIAL_CLOSURE',
      predicted_materially_disruptive: false,
      observed_materially_disruptive: false,
      predicted_supply_at_risk_percent: 8.4,
      predicted_confidence: 0.7,
    },
  ],
}

export const mockFeedbackEntry = {
  feedback_id: 'FB-000001',
  recommendation_id: 'REC-SCN-20260710-0001',
  useful: true,
  action_taken: 'ACCEPTED',
  rejection_reason: null,
  submitted_by: 'analyst-demo',
  submitted_at: '2026-07-10T09:10:00Z',
}

export const mockModelVersions = [
  {
    model_id: 'risk-scoring-v1',
    model_name: 'risk-scoring',
    version: '0.1',
    status: 'ACTIVE',
    trained_at: '2026-07-01T00:00:00Z',
    training_data_range: '2019-2024 seeded cases',
    metrics: { precision: 0.8, recall: 0.75 },
    owner: 'Abhishek Choudhary',
  },
]

export const mockCommodityEntities = {
  commodity_type: 'CRUDE_OIL',
  entity_count: 5,
  entities: [
    { entity_type: 'SUPPLIER_COUNTRY', entity_id: 'SUP_IRQ', name: 'Iraq' },
    { entity_type: 'SUPPLIER_COUNTRY', entity_id: 'SUP_KSA', name: 'Saudi Arabia' },
    { entity_type: 'CHOKEPOINT', entity_id: 'CHK_HORMUZ', name: 'Strait of Hormuz' },
    { entity_type: 'REFINERY', entity_id: 'REF_JAM', name: 'Reliance Jamnagar' },
    { entity_type: 'STRATEGIC_RESERVE_SITE', entity_id: 'SPR_MAN', name: 'Mangalore SPR' },
  ],
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
