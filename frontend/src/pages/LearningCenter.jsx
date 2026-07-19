import { useEffect, useState } from 'react'
import { activateModel, getLearningCases, getModels, runBacktest } from '../api/energyShieldApi'

export default function LearningCenter() {
  const [cases, setCases] = useState([])
  const [models, setModels] = useState([])
  const [backtestReport, setBacktestReport] = useState(null)
  const [error, setError] = useState(null)
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

  return (
    <div className="page page-learning-center">
      <div className="page-header">
        <h1>Learning Center</h1>
      </div>
      {error && <p className="error-banner">{error}</p>}

      <section className="panel">
        <h2>Historical disruption cases</h2>
        <ul className="data-list compact">
          {cases.map((disruptionCase) => (
            <li key={disruptionCase.case_id}>
              <strong>{disruptionCase.case_name}</strong>
              <span>
                {disruptionCase.start_date} to {disruptionCase.end_date ?? 'ongoing'} - {disruptionCase.commodity_type}
              </span>
              <span>
                Observed: {disruptionCase.observed_outcomes.average_delay_days}d delay,{' '}
                {disruptionCase.observed_outcomes.freight_cost_increase_percent}% freight cost
              </span>
            </li>
          ))}
          {!cases.length && <li>No historical cases loaded.</li>}
        </ul>
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
            <ul className="metric-list">
              <li>
                <span>Precision</span>
                <strong>{backtestReport.precision}</strong>
              </li>
              <li>
                <span>Recall</span>
                <strong>{backtestReport.recall}</strong>
              </li>
              <li>
                <span>False alarm rate</span>
                <strong>{backtestReport.false_alarm_rate}</strong>
              </li>
              <li>
                <span>Missed event rate</span>
                <strong>{backtestReport.missed_event_rate}</strong>
              </li>
            </ul>
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
                  <span className="pill">{model.status}</span>
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
      </section>
    </div>
  )
}
