import { useState } from 'react'
import { runScenario } from '../api/energyShieldApi'
import ScenarioResultPanel from '../components/scenarios/ScenarioResultPanel'
import { humanize } from '../utils/format'

const SCENARIO_TYPES = [
  'HORMUZ_PARTIAL_CLOSURE',
  'RED_SEA_SHIPPING_DISRUPTION',
  'OPEC_SUPPLY_CUT',
  'SANCTIONS_SHOCK',
  'PORT_CONGESTION',
  'LNG_SUPPLY_SHOCK',
  'COAL_IMPORT_DISRUPTION',
  'FERTILIZER_FEEDSTOCK_SHOCK',
  'CRITICAL_MINERAL_EXPORT_RESTRICTION',
]

const SEVERITY_LEVELS = ['LOW', 'MEDIUM', 'HIGH', 'SEVERE', 'CRITICAL']

const COMMODITY_FOR_SCENARIO = {
  LNG_SUPPLY_SHOCK: 'LNG',
  COAL_IMPORT_DISRUPTION: 'COAL',
  FERTILIZER_FEEDSTOCK_SHOCK: 'FERTILIZER',
  CRITICAL_MINERAL_EXPORT_RESTRICTION: 'CRITICAL_MINERALS',
}

export default function ScenarioSimulator() {
  const [form, setForm] = useState({
    scenario_type: SCENARIO_TYPES[0],
    duration_days: 15,
    severity: 'HIGH',
    affected_entities: '',
    supply_reduction_percent: '',
    freight_cost_increase_percent: '',
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const manual_overrides = {}
      if (form.supply_reduction_percent !== '') {
        manual_overrides.supply_reduction_percent = Number(form.supply_reduction_percent)
      }
      if (form.freight_cost_increase_percent !== '') {
        manual_overrides.freight_cost_increase_percent = Number(form.freight_cost_increase_percent)
      }

      const payload = {
        scenario_type: form.scenario_type,
        commodity_type: COMMODITY_FOR_SCENARIO[form.scenario_type] ?? 'CRUDE_OIL',
        duration_days: Number(form.duration_days),
        severity: form.severity,
        affected_entities: form.affected_entities
          .split(',')
          .map((entity) => entity.trim())
          .filter(Boolean),
        manual_overrides,
      }
      const scenario = await runScenario(payload)
      setResult(scenario)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page page-scenario-simulator">
      <div className="page-header">
        <div>
          <h1>Scenario Simulator</h1>
          <p className="page-header__copy">Model a disruption and see supply, delay, cost, and refinery impact.</p>
        </div>
      </div>

      <section className="card-grid">
        <form className="panel scenario-form" onSubmit={handleSubmit}>
          <h2>Run a scenario</h2>

          <label htmlFor="scenario_type">Scenario type</label>
          <select
            id="scenario_type"
            value={form.scenario_type}
            onChange={(event) => update('scenario_type', event.target.value)}
          >
            {SCENARIO_TYPES.map((type) => (
              <option key={type} value={type}>
                {humanize(type)}
              </option>
            ))}
          </select>

          <div className="form-row">
            <div>
              <label htmlFor="severity">Severity</label>
              <select id="severity" value={form.severity} onChange={(event) => update('severity', event.target.value)}>
                {SEVERITY_LEVELS.map((level) => (
                  <option key={level} value={level}>
                    {humanize(level)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="duration_days">Duration (days)</label>
              <input
                id="duration_days"
                type="number"
                min={1}
                value={form.duration_days}
                onChange={(event) => update('duration_days', event.target.value)}
              />
            </div>
          </div>

          <label htmlFor="affected_entities">Affected entity ids (comma-separated, optional)</label>
          <input
            id="affected_entities"
            type="text"
            placeholder="e.g. CHK_HORMUZ"
            value={form.affected_entities}
            onChange={(event) => update('affected_entities', event.target.value)}
          />
          <p className="field-hint">Leave blank to let the scenario template resolve its own affected entities.</p>

          <details>
            <summary>Manual overrides (optional)</summary>
            <div className="form-row">
              <div>
                <label htmlFor="supply_reduction_percent">Supply reduction %</label>
                <input
                  id="supply_reduction_percent"
                  type="number"
                  value={form.supply_reduction_percent}
                  onChange={(event) => update('supply_reduction_percent', event.target.value)}
                />
              </div>
              <div>
                <label htmlFor="freight_cost_increase_percent">Freight cost increase %</label>
                <input
                  id="freight_cost_increase_percent"
                  type="number"
                  value={form.freight_cost_increase_percent}
                  onChange={(event) => update('freight_cost_increase_percent', event.target.value)}
                />
              </div>
            </div>
          </details>

          <button type="submit" className="primary-button" disabled={loading} style={{ marginTop: 'var(--space-3)' }}>
            {loading ? 'Running...' : 'Run scenario'}
          </button>
          {error && <p className="error-banner">{error}</p>}
        </form>

        <div className="panel">
          <h2>Result</h2>
          <ScenarioResultPanel result={result} />
        </div>
      </section>
    </div>
  )
}
