// Renders the audit trail UI listing audit events for entities such as events, scenarios, recommendations, and overrides.
export default function AuditLogTable({ entries }) {
  if (!entries?.length) {
    return <div className="component component-audit-log-table component--empty">No audit entries for this entity yet.</div>
  }

  return (
    <div className="component component-audit-log-table">
      <table className="data-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Action</th>
            <th>Entity</th>
            <th>Summary</th>
            <th>Actor</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.audit_id}>
              <td>{new Date(entry.timestamp).toLocaleString()}</td>
              <td>
                <span className="pill">{entry.action}</span>
              </td>
              <td>
                {entry.entity_type} - {entry.entity_id}
              </td>
              <td>{entry.summary}</td>
              <td>{entry.actor}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
