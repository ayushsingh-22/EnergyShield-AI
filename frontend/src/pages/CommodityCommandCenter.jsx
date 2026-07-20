import { useEffect, useState } from 'react'
import { getCommodities, getCommodityEntities, getCommodityRisk, getCommodityScenarios } from '../api/energyShieldApi'
import CommoditySelector from '../components/commodities/CommoditySelector'
import { SkeletonList } from '../components/layout/Skeleton'
import RiskScoreCard from '../components/risk/RiskScoreCard'
import { humanize } from '../utils/format'

export default function CommodityCommandCenter() {
  const [commodities, setCommodities] = useState([])
  const [selected, setSelected] = useState(null)
  const [entities, setEntities] = useState(null)
  const [risk, setRisk] = useState([])
  const [scenarioTemplates, setScenarioTemplates] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [entityLoading, setEntityLoading] = useState(true)

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
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!selected) return
    let cancelled = false
    setEntityLoading(true)
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
      .finally(() => {
        if (!cancelled) setEntityLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [selected])

  const selectedDefinition = commodities.find((c) => c.commodity_type === selected)

  return (
    <div className="page page-commodity-command-center">
      <div className="page-header">
        <div>
          <h1>Commodity Command Center</h1>
          <p className="page-header__copy">Switch commodities to see their own entities, risk, and scenario templates.</p>
        </div>
      </div>
      {error && <p className="error-banner">{error}</p>}

      {loading ? (
        <SkeletonList rows={1} />
      ) : (
        <CommoditySelector commodities={commodities} selected={selected} onSelect={setSelected} />
      )}

      {selectedDefinition && (
        <section className="card-grid">
          <article className="panel">
            <h2>{selectedDefinition.display_name}</h2>
            <p className="panel-copy">Unit: {selectedDefinition.unit}</p>
            <h3>Scenario templates</h3>
            {entityLoading ? (
              <SkeletonList rows={2} />
            ) : (
              <ul className="data-list compact">
                {scenarioTemplates.map((template) => (
                  <li key={template}>{humanize(template)}</li>
                ))}
                {!scenarioTemplates.length && <li>No scenario templates for this commodity yet.</li>}
              </ul>
            )}
          </article>

          <article className="panel">
            <h2>Supply chain entities</h2>
            <p className="panel-copy">{entities?.entity_count ?? 0} entities loaded.</p>
            {entityLoading ? (
              <SkeletonList rows={2} />
            ) : (
              <ul className="data-list compact">
                {entities?.entities?.map((entity) => (
                  <li key={entity.entity_id}>
                    <strong>{entity.name}</strong>
                    <span>{humanize(entity.entity_type)}</span>
                    {entity.is_simulated && <span className="tag tag--simulated">simulated</span>}
                  </li>
                ))}
                {!entities?.entities?.length && <li>No entities loaded for this commodity yet.</li>}
              </ul>
            )}
          </article>

          <article className="panel">
            <h2>Risk cards</h2>
            {entityLoading ? (
              <div className="risk-card-grid">
                <SkeletonList rows={2} />
              </div>
            ) : (
              <div className="risk-card-grid">
                {risk.map((score) => (
                  <RiskScoreCard key={score.entity_id} score={score} />
                ))}
                {!risk.length && <p className="panel-copy">No risk scores available for this commodity yet.</p>}
              </div>
            )}
          </article>
        </section>
      )}
    </div>
  )
}
