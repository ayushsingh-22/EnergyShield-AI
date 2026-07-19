// Renders the explanation UI showing top drivers and evidence behind a risk score, scenario result, or recommendation.
export default function ExplainabilityPanel({ score }) {
  if (!score) {
    return (
      <div className="component component-explainability-panel component--empty">
        Select a risk score to see why it was generated.
      </div>
    )
  }

  return (
    <div className="component component-explainability-panel">
      <h4>
        Why is {score.entity_id} {score.risk_level}?
      </h4>
      <p className="panel-copy">
        Score {score.risk_score}/100, confidence {Math.round((score.confidence ?? 0) * 100)}%.
      </p>
      <h5>Top drivers</h5>
      <ul className="assumption-list">
        {score.top_drivers?.length ? (
          score.top_drivers.map((driver, index) => <li key={index}>{driver}</li>)
        ) : (
          <li>No active drivers - score reflects baseline exposure only.</li>
        )}
      </ul>
      <h5>Evidence events</h5>
      {score.evidence_event_ids?.length ? (
        <ul className="assumption-list">
          {score.evidence_event_ids.map((eventId) => (
            <li key={eventId}>{eventId}</li>
          ))}
        </ul>
      ) : (
        <p className="panel-copy">No linked evidence events.</p>
      )}
      <h5>Assumptions</h5>
      <ul className="assumption-list">
        {score.assumptions?.map((assumption, index) => (
          <li key={index}>
            {assumption.description}
            {assumption.is_simulated ? <span className="tag tag--simulated">simulated</span> : null}
          </li>
        ))}
      </ul>
    </div>
  )
}
