import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { getCorridorRisk, getRiskHistory, getSupplierRisk } from '../api/energyShieldApi'
import { useEntityName } from '../context/EntityNamesContext'
import { SkeletonList } from '../components/layout/Skeleton'
import ExplainabilityPanel from '../components/risk/ExplainabilityPanel'
import EvidenceEventsModal from '../components/risk/EvidenceEventsModal'
import RiskScoreCard from '../components/risk/RiskScoreCard'

export default function RiskMonitor() {
  const resolveName = useEntityName()
  const [corridorRisk, setCorridorRisk] = useState([])
  const [supplierRisk, setSupplierRisk] = useState([])
  const [selected, setSelected] = useState(null)
  const [history, setHistory] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [evidenceEventIds, setEvidenceEventIds] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const [corridors, suppliers] = await Promise.all([getCorridorRisk(), getSupplierRisk()])
        if (cancelled) return
        setCorridorRisk(corridors)
        setSupplierRisk(suppliers)
        setSelected(corridors[0] ?? suppliers[0] ?? null)
      } catch (err) {
        if (!cancelled) setError(err.message)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!selected) return
    let cancelled = false
    getRiskHistory(selected.entity_id)
      .then((data) => {
        if (!cancelled) setHistory(data)
      })
      .catch(() => {
        if (!cancelled) setHistory([])
      })
    return () => {
      cancelled = true
    }
  }, [selected])

  const chartData = history.map((point) => ({
    updated_at: new Date(point.updated_at).toLocaleDateString(),
    risk_score: point.risk_score,
  }))

  return (
    <div className="page page-risk-monitor">
      <div className="page-header">
        <div>
          <h1>Risk Monitor</h1>
          <p className="page-header__copy">Select a card to see its score history and full explainability.</p>
        </div>
      </div>
      {error && <p className="error-banner">{error}</p>}

      <section className="panel">
        <h2>Corridors</h2>
        {loading ? (
          <div className="risk-card-grid">
            <SkeletonList rows={3} />
          </div>
        ) : (
          <div className="risk-card-grid">
            {corridorRisk.map((score) => (
              <div
                key={score.entity_id}
                onClick={() => setSelected(score)}
                onKeyDown={(event) => (event.key === 'Enter' || event.key === ' ') && setSelected(score)}
                role="button"
                tabIndex={0}
              >
                <RiskScoreCard
                  score={score}
                  selected={score.entity_id === selected?.entity_id}
                  onSelectEvidence={setEvidenceEventIds}
                />
              </div>
            ))}
            {!corridorRisk.length && <p className="panel-copy">No corridor scores available yet.</p>}
          </div>
        )}
      </section>

      <section className="panel">
        <h2>Suppliers</h2>
        {loading ? (
          <div className="risk-card-grid">
            <SkeletonList rows={2} />
          </div>
        ) : (
          <div className="risk-card-grid">
            {supplierRisk.map((score) => (
              <div
                key={score.entity_id}
                onClick={() => setSelected(score)}
                onKeyDown={(event) => (event.key === 'Enter' || event.key === ' ') && setSelected(score)}
                role="button"
                tabIndex={0}
              >
                <RiskScoreCard
                  score={score}
                  selected={score.entity_id === selected?.entity_id}
                  onSelectEvidence={setEvidenceEventIds}
                />
              </div>
            ))}
            {!supplierRisk.length && <p className="panel-copy">No supplier scores available yet.</p>}
          </div>
        )}
      </section>

      <section className="card-grid">
        <article className="panel">
          <h2>Score history {selected ? `- ${resolveName(selected.entity_id)}` : ''}</h2>
          {chartData.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-hairline)" />
                <XAxis dataKey="updated_at" tick={{ fill: 'var(--ink-muted)', fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fill: 'var(--ink-muted)', fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="risk_score" stroke="var(--series-6)" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="panel-copy">No history yet for this entity.</p>
          )}
        </article>

        <article className="panel">
          <h2>Explainability</h2>
          <ExplainabilityPanel score={selected} onSelectEvidence={setEvidenceEventIds} />
        </article>
      </section>

      {evidenceEventIds && (
        <EvidenceEventsModal eventIds={evidenceEventIds} onClose={() => setEvidenceEventIds(null)} />
      )}
    </div>
  )
}
