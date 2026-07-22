import { useState } from 'react'
import { generateReport, getAuditTrail } from '../api/energyShieldApi'
import AuditLogTable from '../components/reports/AuditLogTable'
import { renderReportMarkdown } from '../utils/markdown'

function formatTimestamp(value) {
  if (!value) return 'n/a'
  return new Date(value).toLocaleString()
}

export default function Reports() {
  const [scenarioId, setScenarioId] = useState('')
  const [report, setReport] = useState(null)
  const [auditEntries, setAuditEntries] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  function handlePrint() {
    window.print()
  }

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
      <div className="page-header report-print-hide">
        <div>
          <h1>Reports</h1>
          <p className="page-header__copy">Generate an executive crisis-response brief and trace its full audit trail.</p>
        </div>
      </div>

      <form className="panel inline-form report-print-hide" onSubmit={handleGenerate}>
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
        <section className="panel report-print-target">
          <div className="report-doc__toolbar">
            <div className="report-doc__toolbar-meta">
              <span className="pill">{report.report_id}</span>
              <span className="report-doc__generated">Generated {formatTimestamp(report.generated_at)}</span>
              {report.is_simulated && <span className="tag tag--simulated">simulated</span>}
            </div>
            <button type="button" className="secondary-button report-print-hide" onClick={handlePrint}>
              Download PDF
            </button>
          </div>

          <article className="report-doc">
            {report.report_markdown ? (
              renderReportMarkdown(report.report_markdown)
            ) : (
              <p className="panel-copy">{report.executive_summary}</p>
            )}
          </article>
        </section>
      )}

      <section className="panel report-print-hide">
        <h2>Audit trail</h2>
        <AuditLogTable entries={auditEntries} />
      </section>
    </div>
  )
}
