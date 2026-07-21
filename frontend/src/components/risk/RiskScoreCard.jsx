// Renders a single corridor/supplier risk score card with score, level, delta, top drivers, and evidence.
import { useEntityName } from '../../context/EntityNamesContext'
import { humanize } from '../../utils/format'

const LEVEL_CLASS = {
  LOW: 'risk-badge risk-badge--low',
  MEDIUM: 'risk-badge risk-badge--medium',
  HIGH: 'risk-badge risk-badge--high',
  SEVERE: 'risk-badge risk-badge--severe',
  CRITICAL: 'risk-badge risk-badge--critical',
}

function formatDelta(delta) {
  if (delta === null || delta === undefined) return 'baseline'
  const sign = delta > 0 ? '+' : ''
  return `${sign}${delta} vs previous`
}

export default function RiskScoreCard({ score, onSelectEvidence, selected = false }) {
  const resolveName = useEntityName()
  if (!score) return null
  const badgeClass = LEVEL_CLASS[score.risk_level] ?? 'risk-badge'
  const rootClass = selected
    ? 'component component-risk-score-card component-risk-score-card--selected'
    : 'component component-risk-score-card'
  const deltaClass =
    score.delta > 0
      ? 'risk-score-card__delta risk-score-card__delta--up'
      : score.delta < 0
        ? 'risk-score-card__delta risk-score-card__delta--down'
        : 'risk-score-card__delta'

  return (
    <div className={rootClass}>
      <div className="risk-score-card__header">
        <span className="risk-score-card__title">
          <strong>{resolveName(score.entity_id)}</strong>
          <span className="risk-score-card__id">{score.entity_id}</span>
        </span>
        <span className={badgeClass}>{humanize(score.risk_level)}</span>
      </div>
      <div className="risk-score-card__score">
        {score.risk_score}
        <span className="risk-score-card__score-max">/100</span>
      </div>
      <p className={deltaClass}>{formatDelta(score.delta)}</p>
      {score.top_drivers?.length ? (
        <ul className="risk-score-card__drivers">
          {score.top_drivers.map((driver, index) => (
            <li key={index}>{driver}</li>
          ))}
        </ul>
      ) : (
        <p className="risk-score-card__drivers-empty">No active risk drivers.</p>
      )}
      <div className="risk-score-card__footer">
        {score.evidence_event_ids?.length ? (
          <button
            type="button"
            className="link-button"
            onClick={() => onSelectEvidence?.(score.evidence_event_ids)}
          >
            {score.evidence_event_ids.length} evidence event(s)
          </button>
        ) : null}
        <p className="risk-score-card__confidence">Confidence {Math.round((score.confidence ?? 0) * 100)}%</p>
      </div>
    </div>
  )
}
