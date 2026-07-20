import { useState } from 'react'
import { getRecommendation, submitFeedback } from '../api/energyShieldApi'
import RecommendationTable from '../components/recommendations/RecommendationTable'

export default function RecommendationCenter() {
  const [scenarioId, setScenarioId] = useState('')
  const [recommendation, setRecommendation] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [feedbackStatus, setFeedbackStatus] = useState(null)

  async function handleLookup(event) {
    event.preventDefault()
    if (!scenarioId.trim()) return
    setLoading(true)
    setError(null)
    setFeedbackStatus(null)
    try {
      const data = await getRecommendation(scenarioId.trim())
      setRecommendation(data)
    } catch (err) {
      setRecommendation(null)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleFeedback(useful) {
    if (!recommendation) return
    try {
      await submitFeedback({
        recommendation_id: recommendation.recommendation_id,
        useful,
        action_taken: useful ? 'ACCEPTED' : 'REJECTED',
      })
      setFeedbackStatus(useful ? 'Marked useful - thank you.' : 'Marked not useful - thank you.')
    } catch (err) {
      setFeedbackStatus(`Could not submit feedback: ${err.message}`)
    }
  }

  return (
    <div className="page page-recommendation-center">
      <div className="page-header">
        <div>
          <h1>Recommendation Center</h1>
          <p className="page-header__copy">Ranked procurement alternatives and SPR drawdown plan for a scenario.</p>
        </div>
      </div>

      <form className="panel inline-form" onSubmit={handleLookup}>
        <div>
          <label htmlFor="scenario-id">Scenario ID</label>
          <input
            id="scenario-id"
            type="text"
            placeholder="e.g. SCN-20260719-0001"
            value={scenarioId}
            onChange={(event) => setScenarioId(event.target.value)}
          />
        </div>
        <button type="submit" className="primary-button" disabled={loading}>
          {loading ? 'Loading...' : 'Load recommendation'}
        </button>
      </form>
      <p className="field-hint">Run a scenario in the Scenario Simulator first, then paste its ID here.</p>
      {error && <p className="error-banner">{error}</p>}

      <section className="panel">
        <h2>Ranked options</h2>
        <RecommendationTable recommendation={recommendation} />
        {recommendation && (
          <div className="feedback-row">
            <span>Was this recommendation useful?</span>
            <button type="button" className="link-button" onClick={() => handleFeedback(true)}>
              Yes
            </button>
            <button type="button" className="link-button" onClick={() => handleFeedback(false)}>
              No
            </button>
            {feedbackStatus && <span className="feedback-row__status">{feedbackStatus}</span>}
          </div>
        )}
      </section>
    </div>
  )
}
