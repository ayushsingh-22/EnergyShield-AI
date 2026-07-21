import { useEffect, useState } from 'react'
import {
  getCorridorRisk,
  getHealth,
  getLatestEvents,
  getSupplierRisk,
} from '../api/energyShieldApi'
import { SkeletonList } from '../components/layout/Skeleton'
import RiskScoreCard from '../components/risk/RiskScoreCard'
import { humanize } from '../utils/format'

function formatTimestamp(value) {
  if (!value) return 'n/a'
  return new Date(value).toLocaleString()
}

function highestLevel(scores) {
  const order = ['LOW', 'MEDIUM', 'HIGH', 'SEVERE', 'CRITICAL']
  return scores.reduce((worst, score) => {
    return order.indexOf(score.risk_level) > order.indexOf(worst) ? score.risk_level : worst
  }, 'LOW')
}

export default function Dashboard() {
  const [state, setState] = useState({
    health: null,
    latestEvents: [],
    corridorRisk: [],
    supplierRisk: [],
    loading: true,
    error: null,
  })

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const [health, latestEvents, corridorRisk, supplierRisk] = await Promise.all([
          getHealth(),
          getLatestEvents(5),
          getCorridorRisk(),
          getSupplierRisk(),
        ])
        if (!cancelled) {
          setState({ health, latestEvents, corridorRisk, supplierRisk, loading: false, error: null })
        }
      } catch (error) {
        if (!cancelled) setState((current) => ({ ...current, loading: false, error: error.message }))
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [])

  const allRisk = [...state.corridorRisk, ...state.supplierRisk]
  const topRisks = [...allRisk].sort((a, b) => b.risk_score - a.risk_score).slice(0, 4)
  const activeEventCount = state.latestEvents.length
  const worstLevel = allRisk.length ? highestLevel(allRisk) : 'LOW'

  let statusPillClass = 'status-pill'
  let statusLabel = 'Connecting...'
  if (state.error) {
    statusPillClass = 'status-pill status-pill--error'
    statusLabel = `Backend error - ${state.error}`
  } else if (state.loading) {
    statusPillClass = 'status-pill status-pill--loading'
    statusLabel = 'Loading live data...'
  } else if (state.health) {
    statusLabel = `Backend ${state.health.status}`
  }

  return (
    <div className="page page-dashboard">
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <h1>Command Center</h1>
            <select
              className="commodity-selector"
              style={{ padding: '0.25rem 0.5rem', borderRadius: '4px', border: '1px solid var(--border)' }}
              defaultValue="CRUDE_OIL"
              onChange={(e) => {
                if (e.target.value !== 'CRUDE_OIL') {
                  alert(`Support for ${e.target.value} is coming in a future expansion. For now, the MVP focuses on Crude Oil.`)
                  e.target.value = 'CRUDE_OIL'
                }
              }}
            >
              <option value="CRUDE_OIL">Crude Oil</option>
              <option value="LNG">LNG</option>
              <option value="COAL">Coal</option>
              <option value="FERTILIZER">Fertilizer</option>
              <option value="CRITICAL_MINERALS">Critical Minerals</option>
            </select>
          </div>
          <p className="page-header__copy">Live overview of corridor/supplier risk and recent signals.</p>
        </div>
        <span className={statusPillClass}>
          <span className="status-pill__dot" aria-hidden="true" />
          {statusLabel}
        </span>
      </div>

      {state.loading ? (
        <div className="kpi-row">
          <SkeletonList rows={4} />
        </div>
      ) : (
        <div className="kpi-row">
          <div className={`kpi-tile ${worstLevel === 'CRITICAL' || worstLevel === 'SEVERE' ? 'kpi-tile--critical' : ''}`}>
            <span className="kpi-tile__label">Highest risk level</span>
            <span className="kpi-tile__value">{humanize(worstLevel)}</span>
            <span className="kpi-tile__sub">{allRisk.length} corridors/suppliers scored</span>
          </div>
          <div className="kpi-tile kpi-tile--accent">
            <span className="kpi-tile__label">Active events</span>
            <span className="kpi-tile__value">{activeEventCount}</span>
            <span className="kpi-tile__sub">Detected in the last feed refresh</span>
          </div>

          <div className="kpi-tile">
            <span className="kpi-tile__label">Top corridor score</span>
            <span className="kpi-tile__value">{topRisks[0]?.risk_score ?? '—'}</span>
            <span className="kpi-tile__sub">{topRisks[0]?.entity_id ?? 'No scores yet'}</span>
          </div>
        </div>
      )}

      <section className="card-grid">
        <article className="panel">
          <h2>Top Risks</h2>
          <p className="panel-copy">Highest-scoring corridors and suppliers right now.</p>
          {state.loading ? (
            <SkeletonList rows={3} />
          ) : (
            <div className="risk-card-grid">
              {topRisks.map((score) => (
                <RiskScoreCard key={score.entity_id} score={score} />
              ))}
              {!topRisks.length && <p className="panel-copy">No risk scores available yet.</p>}
            </div>
          )}
        </article>

        <article className="panel">
          <h2>Latest Events</h2>
          <p className="panel-copy">Most recently detected structured risk events.</p>
          {state.loading ? (
            <SkeletonList rows={3} />
          ) : (
            <ul className="data-list compact">
              {state.latestEvents.map((event) => (
                <li key={event.event_id}>
                  <strong>{event.title}</strong>
                  <span>
                    {humanize(event.event_type)} - severity {event.severity} - confidence{' '}
                    {Math.round((event.confidence ?? 0) * 100)}%
                  </span>
                  <span>
                    {event.source_name} ({humanize(event.source_reliability)}) - {formatTimestamp(event.detected_at)}
                  </span>
                </li>
              ))}
              {!state.latestEvents.length && <li>No events detected yet.</li>}
            </ul>
          )}
        </article>

      </section>

      <section className="panel">
        <h2>Where to go next</h2>
        <p className="panel-copy">
          Run a disruption scenario in <strong>Scenario Simulator</strong>, then review the ranked
          procurement/SPR plan in <strong>Recommendations</strong>. Every generated output is traceable
          in <strong>Reports</strong>'s audit trail.
        </p>
      </section>
    </div>
  )
}
