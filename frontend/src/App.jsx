import { useEffect, useState } from 'react'
import {
  getAlternativeSuppliers,
  getCorridorRisk,
  getDataFreshness,
  getDigitalTwinExposure,
  getDigitalTwinMap,
  getHealth,
  getLatestEvents,
  getRefineriesExposed,
  getSupplierRisk,
} from './api/energyShieldApi'
import ProjectBrand from './components/layout/ProjectBrand'
import './App.css'

const GRAPH_DEMO_CHOKEPOINT = 'CHK_HORMUZ'
const GRAPH_DEMO_SUPPLIER = 'SUP_IRQ'
const GRAPH_DEMO_COMMODITY = 'CRUDE_OIL'

const ENTITY_TYPE_LABELS = {
  ExportPort: 'Export ports',
  ImportPort: 'Import ports',
  Refinery: 'Refineries',
  SPR: 'SPR sites',
  ShippingRoute: 'Shipping routes',
  Chokepoint: 'Chokepoints',
}

function formatTimestamp(value) {
  if (!value) return 'n/a'
  return new Date(value).toLocaleString()
}

function countMapEntities(mapData) {
  const counts = Object.fromEntries(Object.values(ENTITY_TYPE_LABELS).map((label) => [label, 0]))
  for (const feature of mapData?.features ?? []) {
    const label = ENTITY_TYPE_LABELS[feature?.properties?.entity_type]
    if (label) counts[label] += 1
  }
  return counts
}

function formatDelta(delta) {
  if (delta === null || delta === undefined) return 'baseline'
  const sign = delta > 0 ? '+' : ''
  return `${sign}${delta} vs previous`
}

function App() {
  const [state, setState] = useState({
    health: null,
    freshness: [],
    mapData: null,
    exposure: null,
    exposedRefineries: [],
    alternativeSuppliers: [],
    latestEvents: [],
    corridorRisk: [],
    supplierRisk: [],
    error: null,
  })

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const [
          health,
          freshness,
          mapData,
          exposure,
          exposedRefineries,
          alternativeSuppliers,
          latestEvents,
          corridorRisk,
          supplierRisk,
        ] = await Promise.all([
          getHealth(),
          getDataFreshness(),
          getDigitalTwinMap(),
          getDigitalTwinExposure(),
          getRefineriesExposed(GRAPH_DEMO_CHOKEPOINT),
          getAlternativeSuppliers(GRAPH_DEMO_SUPPLIER, GRAPH_DEMO_COMMODITY),
          getLatestEvents(10),
          getCorridorRisk(),
          getSupplierRisk(),
        ])

        if (!cancelled) {
          setState({
            health,
            freshness,
            mapData,
            exposure,
            exposedRefineries,
            alternativeSuppliers,
            latestEvents,
            corridorRisk,
            supplierRisk,
            error: null,
          })
        }
      } catch (error) {
        if (!cancelled) {
          setState((current) => ({ ...current, error: error.message }))
        }
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [])

  const mapCounts = countMapEntities(state.mapData)

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <div className="hero-brand-block">
          <ProjectBrand subtitle="Phase 1 to Phase 5 audit view" />
          <p className="hero-copy">
            Current UI snapshot for the implemented ingestion foundation, digital twin,
            knowledge graph, event extraction, and risk scoring layers.
          </p>
        </div>
        <div className="status-pill">
          Backend status:{' '}
          {state.error ? `error - ${state.error}` : state.health ? state.health.status : 'loading'}
        </div>
      </section>

      <section className="card-grid">
        <article className="panel">
          <h2>Phase 1 Data Freshness</h2>
          <p className="panel-copy">Live source registry and freshness endpoint output.</p>
          <ul className="data-list">
            {state.freshness.map((source) => (
              <li key={source.source_name}>
                <strong>{source.source_name}</strong>
                <span>{source.reliability_tier}</span>
                <span>{formatTimestamp(source.last_successful_fetch_at)}</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Phase 2 Digital Twin Coverage</h2>
          <p className="panel-copy">Map payload counts derived from /digital-twin/map.</p>
          <ul className="metric-list">
            {Object.entries(mapCounts).map(([label, value]) => (
              <li key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Exposure Baseline</h2>
          <p className="panel-copy">Aggregated phase 2 exposure summary from the backend.</p>
          <ul className="metric-list">
            <li>
              <span>Total supplier exposure</span>
              <strong>{state.exposure?.total_supplier_exposure_percent ?? 'n/a'}%</strong>
            </li>
            <li>
              <span>Total refineries</span>
              <strong>{state.exposure?.total_refineries ?? 'n/a'}</strong>
            </li>
            <li>
              <span>Total SPR capacity</span>
              <strong>{state.exposure?.total_spr_capacity_mmbbl ?? 'n/a'} MMBbl</strong>
            </li>
          </ul>
        </article>

        <article className="panel">
          <h2>Phase 3 Exposed Refineries</h2>
          <p className="panel-copy">Graph query for refineries exposed to {GRAPH_DEMO_CHOKEPOINT}.</p>
          <ul className="data-list compact">
            {state.exposedRefineries.map((refinery) => (
              <li key={refinery.entity_id}>
                <strong>{refinery.name}</strong>
                <span>{refinery.entity_id}</span>
                <span>{refinery.via_route_id ?? refinery.risk_level ?? 'linked'}</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Alternative Suppliers</h2>
          <p className="panel-copy">
            Graph fallback suppliers for {GRAPH_DEMO_SUPPLIER} in {GRAPH_DEMO_COMMODITY}.
          </p>
          <ul className="data-list compact">
            {state.alternativeSuppliers.map((supplier) => (
              <li key={supplier.entity_id}>
                <strong>{supplier.name}</strong>
                <span>{supplier.region}</span>
                <span>{supplier.import_share_percent ?? 'n/a'}%</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Phase 4 Latest Events</h2>
          <p className="panel-copy">Structured risk events from /events/latest.</p>
          <ul className="data-list compact">
            {state.latestEvents.map((event) => (
              <li key={event.event_id}>
                <strong>{event.title}</strong>
                <span>
                  {event.event_type} - severity {event.severity} - confidence{' '}
                  {Math.round((event.confidence ?? 0) * 100)}%
                </span>
                <span>
                  {event.source_name} ({event.source_reliability}) - {formatTimestamp(event.detected_at)}
                </span>
              </li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Phase 5 Corridor Risk</h2>
          <p className="panel-copy">Live chokepoint/route risk scores from /risk/corridors.</p>
          <ul className="data-list compact">
            {state.corridorRisk.map((score) => (
              <li key={score.entity_id}>
                <strong>
                  {score.entity_id} - {score.risk_score} ({score.risk_level})
                </strong>
                <span>{formatDelta(score.delta)}</span>
                <span>{score.top_drivers?.[0] ?? 'No active risk events'}</span>
              </li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Phase 5 Supplier Risk</h2>
          <p className="panel-copy">Live supplier country risk scores from /risk/suppliers.</p>
          <ul className="data-list compact">
            {state.supplierRisk.map((score) => (
              <li key={score.entity_id}>
                <strong>
                  {score.entity_id} - {score.risk_score} ({score.risk_level})
                </strong>
                <span>{formatDelta(score.delta)}</span>
                <span>{score.top_drivers?.[0] ?? 'No active risk events'}</span>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  )
}

export default App
