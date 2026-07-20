// Renders scenario simulation outputs including supply at risk, delay, cost impact, affected refineries, and confidence.
import { useEntityName } from '../../context/EntityNamesContext'
import { humanize } from '../../utils/format'

export default function ScenarioResultPanel({ result }) {
  const resolveName = useEntityName()
  if (!result) {
    return (
      <div className="component component-scenario-result-panel component--empty">
        Run a scenario to see its impact estimate here.
      </div>
    )
  }

  return (
    <div className="component component-scenario-result-panel">
      <div className="scenario-result__header">
        <h3>{humanize(result.scenario_type)}</h3>
        <span className="pill">{result.scenario_id}</span>
      </div>

      <div className="scenario-result__metrics">
        <div className="metric">
          <span className="metric__label">Supply at risk</span>
          <strong className="metric__value">{result.supply_at_risk_percent}%</strong>
        </div>
        <div className="metric">
          <span className="metric__label">Estimated delay</span>
          <strong className="metric__value">{result.estimated_delay_days}d</strong>
        </div>
        <div className="metric">
          <span className="metric__label">Freight cost impact</span>
          <strong className="metric__value">{result.freight_cost_impact_percent}%</strong>
        </div>
        <div className="metric">
          <span className="metric__label">Confidence</span>
          <strong className="metric__value">{Math.round((result.confidence ?? 0) * 100)}%</strong>
        </div>
      </div>

      {result.recommended_action_required ? (
        <p className="scenario-result__action-flag">Action required</p>
      ) : (
        <p className="scenario-result__action-flag scenario-result__action-flag--calm">Manageable without SPR action</p>
      )}

      <h4>Affected refineries</h4>
      {result.affected_refineries?.length ? (
        <ul className="data-list compact">
          {result.affected_refineries.map((refinery) => (
            <li key={refinery.refinery_id}>
              <strong>
                {resolveName(refinery.refinery_id)} - {humanize(refinery.exposure_level)}
              </strong>
              <span>{refinery.reason}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="panel-copy">No specific refinery exposure resolved.</p>
      )}

      <h4>Assumptions</h4>
      <ul className="assumption-list">
        {result.assumptions?.map((assumption, index) => (
          <li key={index}>
            {assumption.description}
            {assumption.is_simulated ? <span className="tag tag--simulated">simulated</span> : null}
          </li>
        ))}
      </ul>
    </div>
  )
}
