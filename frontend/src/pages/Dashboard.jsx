import { useEffect, useState } from 'react'
import {
  getCorridorRisk,
  getDataFreshness,
  getHealth,
  getLatestEvents,
  getSupplierRisk,
} from '../api/energyShieldApi'
import RiskScoreCard from '../components/risk/RiskScoreCard'

function formatTimestamp(value) {
  if (!value) return 'n/a'
  return new Date(value).toLocaleString()
}

export default function Dashboard() {
  const [state, setState] = useState({
    health: null,
    freshness: [],
    latestEvents: [],
    corridorRisk: [],
    supplierRisk: [],
    error: null,
  })

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const [health, freshness, latestEvents, corridorRisk, supplierRisk] = await Promise.all([
          getHealth(),
          getDataFreshness(),
          getLatestEvents(5),
          getCorridorRisk(),
          getSupplierRisk(),
        ])
        if (!cancelled) {
          setState({ health, freshness, latestEvents, corridorRisk, supplierRisk, error: null })
        }
      } catch (error) {
        if (!cancelled) setState((current) => ({ ...current, error: error.message }))
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [])

  const topRisks = [...state.corridorRisk, ...state.supplierRisk]
    .sort((a, b) => b.risk_score - a.risk_score)
    .slice(0, 4)

  return (
    <div className="page page-dashboard">
      <div className="page-header">
        <h1>Command Center</h1>
        <span className="status-pill">
          Backend status: {state.error ? `error - ${state.error}` : state.health ? state.health.status : 'loading'}
        </span>
      </div>

      <section className="card-grid">
        <article className="panel">
          <h2>Top Risks</h2>
          <p className="panel-copy">Highest-scoring corridors and suppliers right now.</p>
          <div className="risk-card-grid">
            {topRisks.map((score) => (
              <RiskScoreCard key={score.entity_id} score={score} />
            ))}
            {!topRisks.length && <p className="panel-copy">No risk scores available yet.</p>}
          </div>
        </article>

        <article className="panel">
          <h2>Latest Events</h2>
          <p className="panel-copy">Most recently detected structured risk events.</p>
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
            {!state.latestEvents.length && <li>No events detected yet.</li>}
          </ul>
        </article>

        <article className="panel">
          <h2>Data Freshness</h2>
          <p className="panel-copy">Source registry health from the ingestion layer.</p>
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
      </section>

      <section className="panel">
        <h2>Where to go next</h2>
        <p className="panel-copy">
          Run a disruption scenario in <strong>Scenario Simulator</strong>, then review the ranked
          procurement/SPR plan in <strong>Recommendations</strong>. Every generated output is traceable
          in <strong>Reports</strong> and <strong>Learning Center</strong>'s audit trail.
        </p>
      </section>
    </div>
  )
}
