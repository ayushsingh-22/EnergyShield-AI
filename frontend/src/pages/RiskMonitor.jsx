import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { getCorridorRisk, getRiskHistory, getSupplierRisk } from '../api/energyShieldApi'
import ExplainabilityPanel from '../components/risk/ExplainabilityPanel'
import RiskScoreCard from '../components/risk/RiskScoreCard'

export default function RiskMonitor() {
  const [corridorRisk, setCorridorRisk] = useState([])
  const [supplierRisk, setSupplierRisk] = useState([])
  const [selected, setSelected] = useState(null)
  const [history, setHistory] = useState([])
  const [error, setError] = useState(null)

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
        <h1>Risk Monitor</h1>
      </div>
      {error && <p className="error-banner">{error}</p>}

      <section className="panel">
        <h2>Corridors</h2>
        <div className="risk-card-grid">
          {corridorRisk.map((score) => (
            <div key={score.entity_id} onClick={() => setSelected(score)} role="button" tabIndex={0}>
              <RiskScoreCard score={score} />
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <h2>Suppliers</h2>
        <div className="risk-card-grid">
          {supplierRisk.map((score) => (
            <div key={score.entity_id} onClick={() => setSelected(score)} role="button" tabIndex={0}>
              <RiskScoreCard score={score} />
            </div>
          ))}
        </div>
      </section>

      <section className="card-grid">
        <article className="panel">
          <h2>Score history {selected ? `- ${selected.entity_id}` : ''}</h2>
          {chartData.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="updated_at" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="risk_score" stroke="var(--accent, #aa3bff)" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="panel-copy">No history yet for this entity.</p>
          )}
        </article>

        <article className="panel">
          <h2>Explainability</h2>
          <ExplainabilityPanel score={selected} />
        </article>
      </section>
    </div>
  )
}
