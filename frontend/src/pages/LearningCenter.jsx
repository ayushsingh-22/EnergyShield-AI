import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { activateModel, getLearningCases, getModels, runBacktest } from '../api/energyShieldApi'
import { SkeletonList } from '../components/layout/Skeleton'
import { humanize } from '../utils/format'

// Categorical series validated with the dataviz skill's validate_palette.js
// (see App.css tokens). Predicted/observed is a two-series comparison, so
// slots 1 and 6 (worst-adjacent-pair-safe distance) are used with a legend.
const PREDICTED_COLOR = 'var(--series-1)'
const OBSERVED_COLOR = 'var(--series-6)'

function metricBars(report) {
  if (!report) return []
  return [
    { metric: 'Precision', value: report.precision },
    { metric: 'Recall', value: report.recall },
    { metric: 'False alarm rate', value: report.false_alarm_rate },
    { metric: 'Missed event rate', value: report.missed_event_rate },
  ]
}

export default function LearningCenter() {
  const [cases, setCases] = useState([])
  const [models, setModels] = useState([])
  const [backtestReport, setBacktestReport] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)

  useEffect(() => {
    let cancelled = false
    Promise.all([getLearningCases(), getModels()])
      .then(([caseList, modelList]) => {
        if (!cancelled) {
          setCases(caseList)
          setModels(modelList)
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  async function handleRunBacktest() {
    setRunning(true)
    setError(null)
    try {
      const report = await runBacktest({})
      setBacktestReport(report)
    } catch (err) {
      setError(err.message)
    } finally {
      setRunning(false)
    }
  }

  async function handleActivate(modelId) {
    try {
      const updated = await activateModel(modelId)
      setModels((current) => current.map((model) => (model.model_id === updated.model_id ? updated : model)))
    } catch (err) {
      setError(err.message)
    }
  }

  const caseChartData = (backtestReport?.case_results ?? []).map((caseResult) => ({
    case_id: caseResult.case_id,
    predicted: Math.round((caseResult.predicted_confidence ?? 0) * 100),
    observed: caseResult.observed_materially_disruptive ? 100 : 0,
  }))

  return (
    <div className="page page-learning-center">
      <div className="page-header">
        <div>
          <h1>Learning Center</h1>
          <p className="page-header__copy">Historical disruptions, backtest fidelity, and active model versions.</p>
        </div>
      </div>
      {error && <p className="error-banner">{error}</p>}

      <section className="panel">
        <h2>Historical disruption cases</h2>
        {loading ? (
          <SkeletonList rows={2} />
        ) : (
          <ul className="data-list compact">
            {cases.map((disruptionCase) => (
              <li key={disruptionCase.case_id}>
                <strong>{disruptionCase.case_name}</strong>
                <span>
                  {disruptionCase.start_date} to {disruptionCase.end_date ?? 'ongoing'} -{' '}
                  {humanize(disruptionCase.commodity_type)}
                </span>
                <span>
                  Observed: {disruptionCase.observed_outcomes.average_delay_days}d delay,{' '}
                  {disruptionCase.observed_outcomes.freight_cost_increase_percent}% freight cost
                </span>
              </li>
            ))}
            {!cases.length && <li>No historical cases loaded.</li>}
          </ul>
        )}
      </section>

      <section className="panel">
        <div className="panel-header-row">
          <h2>Backtest</h2>
          <button type="button" className="primary-button" onClick={handleRunBacktest} disabled={running}>
            {running ? 'Running...' : 'Run backtest'}
          </button>
        </div>
        {backtestReport ? (
          <>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={metricBars(backtestReport)} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border-hairline)" />
                <XAxis type="number" domain={[0, 1]} tick={{ fill: 'var(--ink-muted)', fontSize: 12 }} />
                <YAxis type="category" dataKey="metric" width={140} tick={{ fill: 'var(--ink-secondary)', fontSize: 12 }} />
                <Tooltip formatter={(value) => `${Math.round(value * 100)}%`} />
                <Bar dataKey="value" fill={PREDICTED_COLOR} radius={[0, 4, 4, 0]} maxBarSize={28} />
              </BarChart>
            </ResponsiveContainer>

            {caseChartData.length > 0 && (
              <>
                <h4>Predicted confidence vs observed outcome</h4>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={caseChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-hairline)" />
                    <XAxis dataKey="case_id" tick={{ fill: 'var(--ink-muted)', fontSize: 11 }} />
                    <YAxis domain={[0, 100]} tick={{ fill: 'var(--ink-muted)', fontSize: 12 }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="predicted" name="Predicted confidence %" fill={PREDICTED_COLOR} radius={[4, 4, 0, 0]} />
                    <Bar dataKey="observed" name="Observed disruptive (100=yes)" fill={OBSERVED_COLOR} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </>
            )}

            <ul className="data-list compact">
              {backtestReport.case_results?.map((caseResult) => (
                <li key={caseResult.case_id}>
                  <strong>{caseResult.case_id}</strong>
                  <span>
                    predicted {caseResult.predicted_materially_disruptive ? 'disruptive' : 'manageable'} - observed{' '}
                    {caseResult.observed_materially_disruptive ? 'disruptive' : 'manageable'}
                  </span>
                </li>
              ))}
            </ul>
          </>
        ) : (
          <p className="panel-copy">No backtest run yet.</p>
        )}
      </section>

      <section className="panel">
        <h2>Model versions</h2>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Model</th>
                <th>Version</th>
                <th>Status</th>
                <th>Metrics</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {models.map((model) => (
                <tr key={model.model_id}>
                  <td>{model.model_name}</td>
                  <td>{model.version}</td>
                  <td>
                    <span className="pill">{humanize(model.status)}</span>
                  </td>
                  <td>{Object.entries(model.metrics ?? {}).map(([k, v]) => `${k}: ${v}`).join(', ')}</td>
                  <td>
                    {model.status !== 'ACTIVE' && (
                      <button type="button" className="link-button" onClick={() => handleActivate(model.model_id)}>
                        Activate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
