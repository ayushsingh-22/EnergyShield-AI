import { useEffect, useState } from 'react'
import {
  getAlternativeSuppliers,
  getDataFreshness,
  getDigitalTwinExposure,
  getDigitalTwinMap,
  getHealth,
  getRefineriesExposed,
} from './api/energyShieldApi'
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

function App() {
  const [state, setState] = useState({
    health: null,
    freshness: [],
    mapData: null,
    exposure: null,
    exposedRefineries: [],
    alternativeSuppliers: [],
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
        ] = await Promise.all([
          getHealth(),
          getDataFreshness(),
          getDigitalTwinMap(),
          getDigitalTwinExposure(),
          getRefineriesExposed(GRAPH_DEMO_CHOKEPOINT),
          getAlternativeSuppliers(GRAPH_DEMO_SUPPLIER, GRAPH_DEMO_COMMODITY),
        ])

        if (!cancelled) {
          setState({
            health,
            freshness,
            mapData,
            exposure,
            exposedRefineries,
            alternativeSuppliers,
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
        <div>
          <p className="eyebrow">Phase 1 to Phase 3 audit view</p>
          <h1>EnergyShield AI</h1>
          <p className="hero-copy">
            Current UI snapshot for the implemented ingestion foundation, digital twin, and
            knowledge graph layers.
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
      </section>
    </main>
  )
}

export default App
