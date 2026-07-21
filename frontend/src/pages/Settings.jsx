import { useEffect, useState } from 'react'
import { getDataFreshness, getHealth } from '../api/energyShieldApi'
import { SkeletonList } from '../components/layout/Skeleton'
import { humanize } from '../utils/format'

function formatTimestamp(value) {
  if (!value) return 'n/a'
  return new Date(value).toLocaleString()
}

export default function Settings() {
  const [state, setState] = useState({
    health: null,
    freshness: [],
    loading: true,
    error: null,
  })

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const [health, freshness] = await Promise.all([getHealth(), getDataFreshness()])
        if (!cancelled) setState({ health, freshness, loading: false, error: null })
      } catch (error) {
        if (!cancelled) setState(cur => ({ ...cur, loading: false, error: error.message }))
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  return (
    <div className="page page-settings">
      <div className="page-header">
        <div>
          <h1>System Settings</h1>
          <p className="page-header__copy">System health, data ingestion status, and administrative settings.</p>
        </div>
      </div>

      <section className="card-grid">
        <article className="panel">
          <h2>Data Freshness</h2>
          <p className="panel-copy">Source registry health from the ingestion layer.</p>
          {state.loading ? (
            <SkeletonList rows={3} />
          ) : state.error ? (
            <div className="error-message" style={{ color: 'var(--red)' }}>{state.error}</div>
          ) : (
            <ul className="data-list">
              {state.freshness.map((source) => (
                <li key={source.source_name}>
                  <strong>{source.source_name}</strong>
                  <span>{humanize(source.reliability_tier)}</span>
                  <span>{formatTimestamp(source.last_successful_fetch_at)}</span>
                </li>
              ))}
              {!state.freshness.length && <li>No source health data yet.</li>}
            </ul>
          )}
        </article>

        <article className="panel">
          <h2>Backend Health</h2>
          <p className="panel-copy">API connectivity and core services.</p>
          {state.loading ? (
             <SkeletonList rows={2} />
          ) : state.health ? (
             <ul className="data-list compact">
                <li><strong>Status</strong> <span>{state.health.status}</span></li>
                <li><strong>Version</strong> <span>{state.health.version}</span></li>
                <li><strong>Timestamp</strong> <span>{formatTimestamp(state.health.timestamp)}</span></li>
             </ul>
          ) : (
            <p>Unavailable</p>
          )}
        </article>
      </section>
    </div>
  )
}
