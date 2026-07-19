// Renders ranked supplier-route and SPR recommendations with confidence, assumptions, and action priority.
const PRIORITY_CLASS = {
  IMMEDIATE: 'pill pill--immediate',
  CONTINGENCY: 'pill pill--contingency',
  MONITOR: 'pill pill--monitor',
}

export default function RecommendationTable({ recommendation }) {
  if (!recommendation) {
    return (
      <div className="component component-recommendation-table component--empty">
        No recommendation generated yet.
      </div>
    )
  }

  return (
    <div className="component component-recommendation-table">
      <table className="data-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Supplier</th>
            <th>Route</th>
            <th>Delay</th>
            <th>Cost impact</th>
            <th>Risk</th>
            <th>Feasibility</th>
            <th>Priority</th>
          </tr>
        </thead>
        <tbody>
          {recommendation.ranked_options?.map((option) => (
            <tr key={option.rank}>
              <td>{option.rank}</td>
              <td>{option.supplier}</td>
              <td>{option.route}</td>
              <td>{option.estimated_delay_days}d</td>
              <td>{option.cost_impact_percent}%</td>
              <td>{option.risk_level}</td>
              <td>{Math.round(option.feasibility_score * 100)}%</td>
              <td>
                <span className={PRIORITY_CLASS[option.action_priority] ?? 'pill'}>{option.action_priority}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {recommendation.spr_plan ? (
        <div className="spr-plan">
          <h4>Strategic reserve plan</h4>
          {recommendation.spr_plan.drawdown_required ? (
            <p>
              Drawdown <strong>{recommendation.spr_plan.drawdown_percent}%</strong> starting day{' '}
              <strong>{recommendation.spr_plan.start_day}</strong>. {recommendation.spr_plan.reason}
            </p>
          ) : (
            <p>No drawdown required. {recommendation.spr_plan.reason}</p>
          )}
        </div>
      ) : null}

      <p className="recommendation-table__confidence">
        Confidence {Math.round((recommendation.confidence ?? 0) * 100)}% - Audit {recommendation.audit_id}
      </p>
    </div>
  )
}
