import { useState } from 'react'
import { generateReport, getAuditTrail } from '../api/energyShieldApi'
import AuditLogTable from '../components/reports/AuditLogTable'

export default function Reports() {
  const [scenarioId, setScenarioId] = useState('')
  const [report, setReport] = useState(null)
  const [auditEntries, setAuditEntries] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleGenerate(event) {
    event.preventDefault()
    if (!scenarioId.trim()) return
    setLoading(true)
    setError(null)
    try {
      const generated = await generateReport(scenarioId.trim())
      setReport(generated)
      const [scenarioAudit, recommendationAudit] = await Promise.all([
        getAuditTrail(generated.scenario_id),
        getAuditTrail(generated.recommendation_id),
      ])
      setAuditEntries([...scenarioAudit, ...recommendationAudit])
    } catch (err) {
      setError(err.message)
      setReport(null)
      setAuditEntries([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page page-reports">
      <div className="page-header">
        <div>
          <h1>Reports</h1>
          <p className="page-header__copy">Generate an executive crisis-response brief and trace its full audit trail.</p>
        </div>
      </div>

      <form className="panel inline-form" onSubmit={handleGenerate}>
        <div>
          <label htmlFor="report-scenario-id">Scenario ID</label>
          <input
            id="report-scenario-id"
            type="text"
            value={scenarioId}
            onChange={(event) => setScenarioId(event.target.value)}
            placeholder="e.g. SCN-20260719-0001"
          />
        </div>
        <button type="submit" className="primary-button" disabled={loading}>
          {loading ? 'Generating...' : 'Generate report'}
        </button>
      </form>
      {error && <p className="error-banner">{error}</p>}

      {report && (
        <section className="panel">
          <h2>{report.title}</h2>
          <p className="panel-copy">{report.executive_summary}</p>
          {report.report_markdown && (
            <pre className="report-markdown">{report.report_markdown}</pre>
          )}
        </section>
      )}

      <section className="panel">
        <h2>Audit trail</h2>
        <AuditLogTable entries={auditEntries} />
      </section>
    </div>
  )
}
