import { useEffect, useState } from 'react'
import { getCommodities, getCommodityEntities, getCommodityRisk, getCommodityScenarios } from '../api/energyShieldApi'
import CommoditySelector from '../components/commodities/CommoditySelector'
import RiskScoreCard from '../components/risk/RiskScoreCard'

export default function CommodityCommandCenter() {
  const [commodities, setCommodities] = useState([])
  const [selected, setSelected] = useState(null)
  const [entities, setEntities] = useState(null)
  const [risk, setRisk] = useState([])
  const [scenarioTemplates, setScenarioTemplates] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    getCommodities()
      .then((list) => {
        if (cancelled) return
        setCommodities(list)
        setSelected(list[0]?.commodity_type ?? null)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!selected) return
    let cancelled = false
    Promise.all([getCommodityEntities(selected), getCommodityRisk(selected), getCommodityScenarios(selected)])
      .then(([entityData, riskData, scenarioData]) => {
        if (cancelled) return
        setEntities(entityData)
        setRisk(riskData)
        setScenarioTemplates(scenarioData)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [selected])

  const selectedDefinition = commodities.find((c) => c.commodity_type === selected)

  return (
    <div className="page page-commodity-command-center">
      <div className="page-header">
        <h1>Commodity Command Center</h1>
      </div>
      {error && <p className="error-banner">{error}</p>}

      <CommoditySelector commodities={commodities} selected={selected} onSelect={setSelected} />

      {selectedDefinition && (
        <section className="card-grid">
          <article className="panel">
            <h2>{selectedDefinition.display_name}</h2>
            <p className="panel-copy">Unit: {selectedDefinition.unit}</p>
            <h3>Scenario templates</h3>
            <ul className="data-list compact">
              {scenarioTemplates.map((template) => (
                <li key={template}>{template}</li>
              ))}
            </ul>
          </article>

          <article className="panel">
            <h2>Supply chain entities</h2>
            <p className="panel-copy">{entities?.entity_count ?? 0} entities loaded.</p>
            <ul className="data-list compact">
              {entities?.entities?.map((entity) => (
                <li key={entity.entity_id}>
                  <strong>{entity.name}</strong>
                  <span>{entity.entity_type}</span>
                  {entity.is_simulated && <span className="tag tag--simulated">simulated</span>}
                </li>
              ))}
            </ul>
          </article>

          <article className="panel">
            <h2>Risk cards</h2>
            <div className="risk-card-grid">
              {risk.map((score) => (
                <RiskScoreCard key={score.entity_id} score={score} />
              ))}
              {!risk.length && <p className="panel-copy">No risk scores available for this commodity yet.</p>}
            </div>
          </article>
        </section>
      )}
    </div>
  )
}
